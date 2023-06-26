import os
import sys
import shutil


import builder.html_vm_report
import builder.html_vm_edit

class VMHandler(object):

    def __init__(self, configData, deleteExistingFiles = False):

        self.errors = []
        self.log =[]
        self.configData = configData
        self.schemaName = configData['schemaName']
        self.restrict_to_project= configData['restrict_to_project']

        self.filesDir = 'src/main/resources/META-INF/resources/templates/screens/'
        self.actionBoxDirSubject = 'xnat_subjectData/actionsBox'
        self.actionBoxDirImage = 'xnat_imageSessionData/actionsBox'
       
        if(deleteExistingFiles):
            self.emptyTheDir()
            self.emptyTheDir()

    def hasError(self):
        return len(self.errors)

    def errors(self):
        return self.errors

    def checkDir(self,vmFile):

        if not os.path.exists(os.path.dirname(vmFile)):
            try:
                os.makedirs(os.path.dirname(vmFile))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def emptyTheDir(self):

        thePath = ('{}/{}/{}').format(self.configData['path_builder_plugins'],self.schemaName, self.filesDir)
        if os.path.exists(thePath):
            self.log.append(' Delete Dir : {}'.format(thePath))
            shutil.rmtree(thePath)


    def loadTemplateReplace(self,templateType,entryType):

        if templateType != 'subject':
            templateType = 'image'

        fname = ('{}/{}_{}_form17.vm'.format(self.configData['path_builder_templates'],templateType,entryType))
        self.log.append(' load file : {}'.format(fname))

        f = open(fname,"r")
        lines = f.readlines()
        f.close()
        return lines

    def pathTemplateReplaceOut(self,templateType,formRef):

        pathPlugin = ('{}/{}'.format(self.configData['path_builder_plugins'],self.schemaName))
        fname = ('{}/{}XDATScreen_{}').format(pathPlugin,self.filesDir,templateType)
        return fname + ('_{}_{}.vm').format(self.configData['schemaName'],formRef)
    
    def copyTemplateScreeen(self):
        src = ('{}/TemplateScreen.vm').format(self.configData['path_builder_templates'])
        dst = ('{}/{}/{}/{}Screen.vm').format(self.configData['path_builder_plugins'], self.schemaName, self.filesDir,self.schemaName.title())
        #shutil.copy(src,dst)

        f = open(src,"r")
        lines = f.readlines()
        f.close()
        f = open(dst, "w")
        for line in lines:
            if '[SCHEMA_NAME]' in line:
                line = line.replace('[SCHEMA_NAME]', self.schemaName.title())
            f.write(line)
        f.close()


    def copyJavascript(self):
        # copy jquery and other scripts into plugin
        js_dest = '{}/{}/src/main/resources/META-INF/resources/scripts/'.format(self.configData['path_builder_plugins'],self.schemaName)
        scriptsDir= ('{}/{}').format(self.configData['path_builder_templates'],'scripts')
        if not os.path.exists(js_dest):
            shutil.copytree( scriptsDir, js_dest , symlinks=False, ignore=None)
            #copy the cusotm javascript
            js_file = ('{}/formmaker.js').format(self.configData['path_builder_templates'])
            shutil.copyfile( js_file,'{}/formmaker{}.js'.format( js_dest,self.configData['schemaName']))

    def copyMacros(self):

        macro_file = ('{}/macros/xMacros.vm').format(self.configData['path_builder_templates'])                          
        macro_dest = '{}/{}/src/main/resources/META-INF/resources/templates/macros/'.format(self.configData['path_builder_plugins'],self.schemaName)

        if not os.path.exists(macro_dest):
            os.makedirs(macro_dest)
        shutil.copyfile( macro_file,'{}/{}Macros.vm'.format( macro_dest,self.configData['schemaName']))

    def handleFormSubforms(self,form,screenType,inputs):

        file_type = '_report_'
        if 'edit' in screenType:
            file_type='_edit_'

        #find all references for subform in forms, and replace
        if len(inputs) == 0 :
            self.errors.append('no inputs')
            return
        formDir = ('{}/{}/{}').format(self.configData['path_builder_plugins'], self.schemaName, self.filesDir)
        for fl in os.listdir(formDir):
            print(fl)
            if file_type in fl:
                print(os.path.join(formDir, fl))
                f = open(os.path.join(formDir, fl), "r")
                lines = f.readlines()
                f.close()
                f = open(os.path.join(formDir, fl), "w")
                for line in lines:
                    if '@{}@'.format(form['ref']) in line:
                        print('REPLACING LINE - ', line)
                        #must be subform type - insert inputs
                        #'line format'  @BASE_SCHEMA@ @SUBFORM NAME form['name']@
                        new_schema_base=line.split("@")[1]
                        #f.write(line)
                        f.write(line.replace(line, '\n'.join(inputs).replace('@BASE_SCHEMA@', new_schema_base)))
                    else:
                        f.write(line)
                f.close()


    def handleFormByExtScreen(self,form,screenType,inputs, jscript=''):

         # print('inputs',inputs)
        if len(inputs) == 0 :
            self.errors.append('no inputs')
            return

        replaceTemplate = self.loadTemplateReplace(form['ext'],screenType)
        writeFileName = self.pathTemplateReplaceOut(screenType,form['ref'])
        
        self.checkDir(writeFileName)
        self.log.append(' write file : {}'.format(writeFileName))

        f = open(writeFileName,"w")

        for line in replaceTemplate:
            if '[HERE_MODIFY_FORM_ACTION]' in line:
                ref = form['ref'][:1].upper() + form['ref'][1:].lower()
                line = line.replace('[HERE_MODIFY_FORM_ACTION]', '{}{}'.format(self.schemaName.title(),ref))
            if '[DATA_TYPE]' in line:
                f.write(line.replace('[DATA_TYPE]','{}:{}'.format(self.schemaName,form['ref'])))
            elif '[HERE_FORM_TITLE]' in line:
                f.write(line.replace('[HERE_FORM_TITLE]', form['name']))
            elif '[HERE_FORM_REF]' in line:
                f.write(line.replace('[HERE_FORM_REF]', form['ref']))
            elif '[HERE_FORM_INPUTS]' in line:
                try:
                    f.write(line.replace('[HERE_FORM_INPUTS]', '\n'.join(inputs)))
                except Exception as e:
                    print('Error writing to {} - error: {}'.format(writeFileName ,e))
                    for n in inputs:
                        print('Error {}'.format(n))
                    sys.exit(0)

            elif '[CUSTOM JAVASCRIPT]' in line:
                f.write(line.replace('[CUSTOM JAVASCRIPT]', '\n'.join(jscript)))
            elif 'xMacro' in line:
                f.write(line.replace('xMacro', '{}Macro'.format(self.schemaName)))
            elif 'formmakerx.js' in line:
                f.write(line.replace('formmakerx.js', 'formmaker{}.js'.format(self.schemaName)))
            else:
                f.write(line)

        f.close()

    def logInput(self,msg,i):
      
        self.log.append(' {} : {} : sub name: {} : form type : {}'.format(msg,i['question'], i['subName'], i['inputFormType']))

    def formEdit(self,form):
  
        inputs = []
        # self.errors.append('eee')
        self.log.append(' loop Form Ext Screens Edit : {}'.format(form['name']) )
        inputs.extend(self.formInputsEdit(form))

        jscript = []
        jscript.extend(self.formJSEdit(form))


        # print('inputs',inputs)
        if len(inputs) == 0 :
            self.errors.append('no inputs')
            return
        if 'subform' in form['ext']:
            print('SUBFORM making form...')
            self.handleFormSubforms(form,'edit', inputs)
        else:
            self.handleFormByExtScreen(form,'edit',inputs, jscript)
        #cop marcos
        self.copyMacros()
        self.copyJavascript()



    def formInputsEdit(self,form):
      #forms=['all forms here']

      out =[]
      subform = False
      if 'subform' in form['ext']:
          subform = True

      for i in form['inputs']:
          out.extend(builder.html_vm_edit.htmlInputEdit(i, self.schemaName, form['ref'], subform))

      return out

    def formJSEdit(self, form):

        out = []
        for i in form['inputs']:
            if 'calc' in i['inputFormType']:
                self.log.append('edit screen CALC : {}'.format(i['question']))
                out.extend(builder.html_vm_edit.editTypeCalcJScript(i,self.schemaName,form['ref']))
        return out

    def formReport(self,form):
  
        inputs = []

        self.log.append(' loop Form Ext Screens Report : {}'.format(form['name']) )
        
        inputs.extend(self.formInputsReport(form))
 
        if len(inputs) == 0 :
            self.errors.append('no inputs')
            return

        if 'subform' in form['ext']:
            print('SUBFORM making form...')
            self.handleFormSubforms(form,'report', inputs)
        else:
            self.handleFormByExtScreen(form,'report',inputs)


    def formInputsReport(self,form):
        subform = False
        if 'subform' in form['ext']:
            subform = True

        out =[]
        for i in form['inputs']:

            el = '{}:{}/{}'.format(self.schemaName,form['ref'],i['dataName'])
            self.log.append('report  screen el : {}'.format(el))
 
            out.extend(builder.html_vm_report.htmlInputReport(i,self.schemaName,form['ref'], subform))

        return out

  



    def add_to_actionsbox(self,form,sequence, version):
        print( 'Making sub-actions box' )
        boxDir = self.actionBoxDirSubject if (form['ext'] == 'subject') else self.actionBoxDirImage      

        fname = ('{}/{}/{}{}/{}_assessors.vm').format(self.configData['path_builder_plugins'],self.schemaName, self.filesDir,boxDir,self.schemaName)      
        self.checkDir(fname)
        if not os.path.isfile(fname):
            try:
                fname = ('{}/action_box_template.vm').format(self.configData['path_builder_templates']) 
                print('assessors.vm does not exist, using template {}'.format(fname))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        f = open(fname,"r")
        lines = f.readlines()
        f.close()

        fname = ('{}/{}/{}{}/{}_assessors.vm').format(self.configData['path_builder_plugins'],self.schemaName, self.filesDir,boxDir,self.schemaName)
        vm_file = ('XDATScreen_edit_{}_{}').format(self.schemaName,form['ref'])        
        f = open(fname,"w")

        for line in lines:
            if '[PROJECT]' in line:
                f.write(line.replace('[PROJECT]', self.restrict_to_project))
            elif '[SCHEMA]' in line:
                f.write(line.replace('[SCHEMA]', self.schemaName))
            else:
                f.write(line)
            if 'ADD_HERE' in line:

                f.write('  <!-- Sequence: {} --> <li class="yuimenuitem"> '.format(sequence))             
                if form['ext'] == 'subject':
                    if '18' in version:
                        f.write('<a href="$link.setPage("{}.vm")'.format(vm_file))
                        f.write('.addQueryData("subjectId", $!om.id).addQueryData("project", $project)">')
                    else:
                        f.write( '<a href="$link.setAction("XDATActionRouter").addPathInfo("xdataction","{}")'.format(vm_file))
                        f.write( '.addPathInfo("search_element","xnat:subjectData").addPathInfo("search_field","xnat:subjectData.ID").addPathInfo("search_value","${om.getId()}").addPathInfo("popup","false").addPathInfo(\'project\',$project)"> ')
                else:
                    f.write('<a href="$link.setAction("XDATActionRouter").addPathInfo("xdataction","{}").addPathInfo("search_element","xnat:imageSessionData")'.format(vm_file))
                    f.write('.addPathInfo("search_field","xnat:imageSessionData.ID").addPathInfo("search_value","${om.getId()}").addPathInfo("popup","false")')
                    f.write('.addPathInfo(\'project\',$project)">' ) 
                f.write(' <div class="ic_spacer">&nbsp;</div>Add {}  </A></li>  \n'.format(form['name'])) 

            
        f.close()
        print ('Created {}'.format(fname)    )
    
    
  