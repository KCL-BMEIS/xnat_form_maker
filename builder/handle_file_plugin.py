import os
import shutil

class PluginHandler(object):

    def __init__(self, configData, deleteExistingFiles = False):

        self.errors = []
        self.log =[]
        self.configData = configData
        self.schemaName = configData['schemaName']

        self.part_plugin_path = 'src/main/java/org/nrg/xnat/plugins/'

    def hasError(self):
        return len(self.errors)

    def errors(self):
        return self.errors



    
    def copyTemplatesReplace(self,toDir):

        fromDir = ('{}/plugin_template'.format(self.configData['path_builder_templates']))

        self.log.append(' copy plugin template from : {}'.format(fromDir))
        self.log.append(' copy plugin template to   : {}'.format(toDir))
        if os.path.exists(toDir):
            shutil.rmtree(toDir)

        shutil.copytree( fromDir,toDir , symlinks=False, ignore=None)

        for root, dirs, files in os.walk(toDir):
            for file in files:
                if file == '.DS_Store':
                    continue
                f_in = os.path.join(root, file)
                # print ('File : ', f_in)
                fxsd = open(f_in,"r")
                lines = fxsd.readlines()
                fxsd.close()
                fxsd = open(f_in,"w")

                for line in lines:
                    fxsd.write(line.replace('[HERE_SCHEMANAME_LOWER]',self.schemaName.lower()).replace('[HERE_SCHEMANAME]',self.schemaName.title()))
              
                fxsd.close()

        for root, dirs, files in os.walk(toDir):
            for file in files:
                fo = os.path.join(root, file)
                if 'Template' in file:                    
                    print ('Renaming {} to {} '.format(file, file.replace('Template',self.schemaName.title()).replace('template',self.schemaName.lower())))
                    os.rename(fo,os.path.join(root, file.replace('Template',self.schemaName.title()).replace('template',self.schemaName.lower())))
                if 'template' in file:
                    print ('Renaming {} to {} '.format(file, file.replace('Template',self.schemaName.title()).replace('template',self.schemaName.lower())))
                    os.rename(fo,os.path.join(root, file.replace('template',self.schemaName.lower())))


    def createFiles(self,forms):
  
        toDir = ('{}/{}/{}{}').format(self.configData['path_builder_plugins'],self.schemaName, self.part_plugin_path,self.configData['schemaName'].lower())
        
        self.copyTemplatesReplace(toDir)

        HERE_IMPORT_BEANS =[]
        HERE_XNAT_DATA_MODELS =[]

        for f in forms:
            sc = self.schemaName[:1].upper() + self.schemaName[1:].lower()
            st = forms[f]['ref'][:1].upper() + forms[f]['ref'][1:].lower()
            bean = '{}{}Bean'.format(sc,st)
            formName = forms[f]['name']
            md = '@XnatDataModel(value = {}.SCHEMA_ELEMENT_NAME, singular = "{}", plural = "{}")'.format(bean,formName,formName)

            HERE_IMPORT_BEANS.append('import org.nrg.xdat.bean.{};'.format(bean) )
            HERE_XNAT_DATA_MODELS.append(md)


        file_plugin = ('{}/plugin/Xnat{}Plugin.java'.format(toDir,self.schemaName.title()))
        print('FILE', file_plugin)
        f = open(file_plugin,"r")
        lines = f.readlines()
        f.close()

        # print(lines)
        self.log.append(' replace file contents : {}'.format(file_plugin))

        f = open(file_plugin,"w")
        for line in lines:
            # print(line)
            if '[HERE_IMPORT_BEANS]' in line:
                f.write(line.replace('[HERE_IMPORT_BEANS]','\n'.join(HERE_IMPORT_BEANS)))
            elif '[HERE_XNAT_DATA_MODELS]' in line:
                f.write(line.replace('[HERE_XNAT_DATA_MODELS]',','.join(HERE_XNAT_DATA_MODELS)))
            elif '[HERE_CLASS_NAME]' in line:
                f.write(line.replace('[HERE_CLASS_NAME]',sc))
            elif '[HERE_SCHEMANAME_LOWER]' in line:
                f.write(line.replace('[HERE_SCHEMANAME_LOWER]',self.configData['schemaName'].lower()))
            elif '[HERE_PLUGIN_NAME]' in line:
                f.write(line.replace('[HERE_PLUGIN_NAME]',self.configData['schemaName']))
            else:
                # print(line)
                f.write(line)

        f.close()

    

