import os
import sys
import subprocess
import shutil
import glob

import configparser as c_parser

import argparse

import builder.loader_xlsx as loader_xlsx
import builder.loader_redcap as loader_redcap
import builder.schema as handle_schema
import builder.handle_vm as handle_vm
import builder.handle_csv as handle_csv
import builder.handle_file_turbine as handle_file_turbine
import builder.handle_file_plugin as handle_file_plugin

test = False


def getConfigSettings(config):

    out = dict()
   
    abs_path = os.path.abspath(__file__)
    parent_dir = os.path.dirname(os.getcwd())
    configFilePath = os.getcwd()

    config.read('xnat.cfg')
    out['version'] = config.get('xnat','xnat_version').replace('.','')
    if '18' in out['version']:
        out['version'] = '176'
    out['path_plugin_builder'] = os.path.dirname(abs_path) 
    out['path_builder_templates'] = os.path.join(out['path_plugin_builder'], 'builder_templates',out['version'])
    out['path_builder_plugins'] = os.path.join(out['path_plugin_builder'], 'plugins')

    out['host'] = config.get('xnat','xnat_host')
    out['path_xnat_plugins'] = config.get('xnat','xnat_home') + '/plugins'
    return out

     

#start some pluginSettings
if sys.version_info < (3, 0):
    config = c_parser.RawConfigParser()
else:
    config = c_parser.ConfigParser()
        
pluginSettings = getConfigSettings(config)




def printArray(msg,data):
    for i in data:
        if sys.version_info < (3, 0):
            print ('{} : {}'.format(msg,i))
        else:
            print('{} : {}'.format(msg,i))

def printHR():
    print('\n ----- \n')

for k in pluginSettings:
    print (' ', k, ' : ',pluginSettings[k])

if __name__ == "__main__":
    """
      Create schema and install datatype. 
      Import data if data exists.
      Reads a template xls file that contains all schema and form data.
      Runs on linux only
    """
        
    sequence = 10 #for actions box
    parsar = argparse.ArgumentParser(description='extract data from XNAT')
    parsar.add_argument('-i',  default='all in folder', help='Input Spreadhseet')
    args = parsar.parse_args()   
    sub=False


    Loader = loader_xlsx.LoaderXlsx(pluginSettings)
    LoaderRedcap = loader_redcap.LoaderRedcap(pluginSettings)

    pathLoadFiles = ('{}/xlsx'.format(pluginSettings['path_plugin_builder']))
    chooseFilesExcell = Loader.filesList(pathLoadFiles)
    pathLoadFilesRC = ('{}/redcap_dict'.format(pluginSettings['path_plugin_builder']))
    LoaderRedcap.dos2unix(pathLoadFilesRC)
    chooseFilesRedcap = LoaderRedcap.filesList(pathLoadFilesRC)
    chooseFiles = chooseFilesExcell + chooseFilesRedcap
    # APPEND CHOOSE FILES HERE WITH REDCAP
    print(chooseFiles)

    if len(chooseFiles) == 0:
        print('No xlsx or redcap dictionary Files Found !')
        exit()
    
    print( '#############################')
    print ('Files reading: {}'.format(chooseFiles))
    for loadFile in chooseFiles:
        pluginSettings['workbook'] = loadFile

        if 'xlsx' in loadFile:
            Loader = loader_xlsx.LoaderXlsx(pluginSettings)
            cleanData = Loader.loadExcel(pathLoadFiles,loadFile)

            #check here for errors
            if Loader.hasError():
                print('############### Errors in ', loadFile)
                printArray('Errors VM ', Loader.errors)
                exit()
        elif 'csv' in loadFile:
            LoaderRedcap = loader_redcap.LoaderRedcap(pluginSettings)
            cleanData = LoaderRedcap.loadRedcap(pathLoadFilesRC, loadFile)

            # check here for errors
            if LoaderRedcap.hasError():
                print('############### Errors in ', loadFile)
                printArray('Errors VM ', LoaderRedcap.errors)
                exit()
        else:
            print('Error: No files found')
            exit()


        schemaName = cleanData['schema']
        pluginSettings['schemaName'] = cleanData['schema']

        #restrict action boxes so only visible in certain projects:
        pluginSettings['restrict_to_project'] = cleanData['restrict_to_project']


        
        # copy gradle files to plugin folder
        templateDir = ('{}/{}/{}').format(pluginSettings['path_plugin_builder'],'gradle_templates', pluginSettings['version'])
        pluginDir = ('{}/{}').format(pluginSettings['path_builder_plugins'],schemaName)     
        if os.path.exists(pluginDir):
            shutil.rmtree(pluginDir)
        shutil.copytree( templateDir, pluginDir , symlinks=False, ignore=None)


                
        #if it a new build need to empty the dirs
        deleteExistingFiles = True

        handleXsd = handle_schema.SchemaHandler(pluginSettings)
        handleVm = handle_vm.VMHandler(pluginSettings,deleteExistingFiles)
        handleTurbine = handle_file_turbine.TurbineHandler(pluginSettings,deleteExistingFiles)
        handlePlugin = handle_file_plugin.PluginHandler(pluginSettings,deleteExistingFiles)
        handleCsv = handle_csv.CSVHandler(pluginSettings, deleteExistingFiles)

        # create schema all forms are in one xsd
        data_xsd = handleXsd.all_data_xsd(cleanData)
        if handleXsd.hasError():
            printArray('Errors Loader ', handleVm.errors)

        handleXsd.write_schema_xsd(schemaName,data_xsd)
        printArray('log schema ', handleXsd.log)
        printHR()
        print( '#############################')
        sequence = 10
        


        # #velocity templates, one for each form
        for f in cleanData['forms']:
            print( '#############################')
            print ('Form: {}-{}'.format(f, cleanData['forms'][f]['name']))
            #print '{}'.format(cleanData['forms'][f])

            print( '##########  MAKING EDIT FORM ################')
            handleVm.formEdit(cleanData['forms'][f])
            if handleVm.hasError():
                printArray('Errors VM ', handleVm.errors)

            print( '##########  MAKING REPORT  ###################')
            handleVm.formReport(cleanData['forms'][f])
            if handleVm.hasError():
                printArray('Errors VM ', handleVm.errors)




            if 'subform' not in cleanData['forms'][f]['ext']:

                print ('########## CREATING ACTIONS BOX  ###################')
                #handleVm.make_actionsbox(cleanData['forms'][f],sequence)

                handleVm.add_to_actionsbox(cleanData['forms'][f],sequence, pluginSettings['version'])
                if handleVm.hasError():
                    printArray('Errors VM ', handleVm.errors)

                handleCsv.writeToFile(cleanData['forms'][f])
                if handleCsv.hasError():
                    printArray('Errors CSV ', handleVm.errors)

                sequence += 1
                #printArray('log VM ', handleVm.log)
                printHR()

                print ('########## CREATING TURBINE FILES  ###################')
                handleTurbine.formEdit(cleanData['forms'][f])
                if handleTurbine.hasError():
                    printArray('Errors Turbine ', handleTurbine.errors)

                #if v1.8, copy TemplateSceen.vm/java
                if '18' in pluginSettings['version']:
                    handleVm.copyTemplateScreeen()
                    if handleVm.hasError():
                        printArray('Errors VM ', handleVm.errors)
                    ### repatsed.... can change so only does once.... but pain as a lot more code

                    handleTurbine.copyTemplateScreeen(cleanData['forms'][f])
                    if handleTurbine.hasError():
                        printArray('Errors Turbine ', handleTurbine.errors)

                    handleTurbine.copyModifyTemplateScreeen(cleanData['forms'][f])
                    if handleTurbine.hasError():
                        printArray('Errors Turbine ', handleTurbine.errors)

                #printArray('log Turbine ', handleTurbine.log)
                printHR()

            if 'subform' in cleanData['forms'][f]['ext']:
                handleCsv.write_subforms(cleanData['forms'][f])
                if handleCsv.hasError():
                    printArray('Errors CSV ', handleVm.errors)

        # exit()
        #write plugin file
        handlePlugin.createFiles(cleanData['forms'])
        printArray('log plugin files ', handlePlugin.log)
        printHR()



        
        #change gradle builde settings.gradle
        gsf = ('{}/settings.gradle').format(templateDir)
        gsfTo = ('{}/settings.gradle').format(pluginDir)
        fgsf = open(gsf,"r")
        lines = fgsf.readlines()
        fgsf.close()

        fgsf = open(gsfTo,"w")
        for line in lines:
            fgsf.write( line.replace('[HERE_SCHEMANAME]',schemaName ) )
        fgsf.close()


        print(' run build ')
        gradlew = 'gradlew'

        #need to restart gradlew in order to clear cache so changes in schema do not break it!!!
        stop_gradlew = '{}/{} --stop'.format(pluginDir, gradlew)
        clean_plugin = '{}/{} clean'.format(pluginDir,gradlew)
        build_plugin = '{}/{} --no-build-cache xnatDataBuilder xnatPluginJar'.format(pluginDir,gradlew )
        if '18' not in pluginSettings['version']:
            build_plugin = '{}/{} --no-build-cache clean jar'.format(pluginDir,gradlew)
        print (' build plugin ',build_plugin)

        
        try:
            suc2 = subprocess.check_call(stop_gradlew, shell=True, cwd=pluginDir)
            suc1 = subprocess.check_call(clean_plugin, shell=True, cwd=pluginDir)
            suc = subprocess.check_call(build_plugin, shell=True, cwd=pluginDir)
            if suc == 0:
                print (' okay, build ')

            fromLoc = '{}/build/libs/{}-plugin*'.format(pluginDir, schemaName)
            for file in glob.glob(r'{}/build/libs/{}*.jar'.format(pluginDir, schemaName)):
                if  'javadoc' not in file and 'sources' not in file and 'beans' not in file:
                    fromLoc = file
                    # in 1.8 different nameing....

            shutil.copy(fromLoc, pluginSettings['path_builder_plugins'])
            toLoc = ('{}/').format(pluginSettings['path_xnat_plugins'])

            if not os.path.isdir(toLoc):
                print ('The plugins directory does not exist, the plugins will not be copied')
            else:
                shutil.copy(fromLoc, toLoc)
                # need to change owner to xnat owner?
                print ('##############################')
                print ('COMPLETED, PLEASE RESTART TOMCAT')
                print ('##############################')


        except Exception as detail:
            print ('failed, build',detail)
            sys.exit(0)
