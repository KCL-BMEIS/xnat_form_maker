import errno
import os
import shutil

class TurbineHandler(object):

    def __init__(self, configData, deleteExistingFiles = False):

        self.errors = []
        self.log =[]
        self.configData = configData
        self.schemaName = configData['schemaName']

        self.filesDir = 'src/main/java/org/apache/turbine/app/xnat/modules/screens/'
        self.actionsDir = 'src/main/java/org/apache/turbine/app/xnat/modules/actions/'

        if(deleteExistingFiles):
            self.emptyTheDir()

    def hasError(self):
        return len(self.errors)


    def checkDir(self,vmFile):

        if not os.path.exists(os.path.dirname(vmFile)):
            try:
                os.makedirs(os.path.dirname(vmFile))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def emptyTheDir(self):

        thePath = ('{}/{}/{}').format(self.configData['path_builder_plugins'],self.schemaName,self.filesDir)
        if os.path.exists(thePath):
            shutil.rmtree(thePath)

            self.log.append(' Empty Dir : {}'.format(thePath))
        thePath = ('{}/{}/{}').format(self.configData['path_builder_plugins'],self.schemaName,self.actionsDir)
        if os.path.exists(thePath):
            shutil.rmtree(thePath)

            self.log.append(' Empty Dir : {}'.format(thePath))

    def copyAndReplace(self,src,dst, form):
        sc = self.schemaName[:1].upper() + self.schemaName[1:].lower()
        st = form['ref'][:1].upper() + form['ref'][1:].lower()
        om_name =  '{}{}'.format(sc, st)
        class_name = 'XDATScreen_edit_{}_{}'.format(self.schemaName, form['ref'])
        label_tag = form['ref']

        f = open(src, "r")
        lines = f.readlines()
        f.close()

        f = open(dst, "w")
        for line in lines:
            if '[SCHEMA_TITLE]'  in line or '[OM_NAME]' in line or '[CLASS_NAME]' in line or '[LABEL_TAG]' in line or '[FORM_NAME]' in line:
                line = line.replace('[OM_NAME]', om_name)
                line = line.replace('[CLASS_NAME]', class_name)
                line = line.replace('[FORM_NAME]', form['ref'])
                line = line.replace('[SCHEMA_TITLE]',self.schemaName.title())
                f.write(line.replace('[LABEL_TAG]', str(label_tag)))
            else:
                f.write(line)

        f.close()

    def loadTemplateReplace(self, form):
         
        fname = ('{}/turbine_java_template.java'.format(self.configData['path_builder_templates']))
        if form['ext'] != 'subject':
            #sesison level
            fname = ('{}/turbine_java_template_session.java'.format(self.configData['path_builder_templates']))
        self.log.append(' load file : {}'.format(fname))

        return fname


    def copyTemplateScreeen(self, form):
        src = ('{}/TemplateScreen.java').format(self.configData['path_builder_templates'])
        dst = ('{}/{}/{}/{}Screen.java').format(self.configData['path_builder_plugins'], self.schemaName, self.filesDir,self.schemaName.title() )
        self.copyAndReplace(src,dst, form)

    def copyModifyTemplateScreeen(self,form):
        #under actions dir
        #for subjects only as dunno about session
        if 'ubject' in form['ext']:

            dst = ('{}/{}/{}/').format(self.configData['path_builder_plugins'], self.schemaName,self.actionsDir)
            if not os.path.exists(os.path.dirname(dst)):
                try:
                    os.makedirs(os.path.dirname(dst))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            self.log.append(' write file : {}'.format(dst))
            #DONT USE title() - as does not work if form contains numbers
            ref = form['ref'][:1].upper() + form['ref'][1:].lower()

            dst = ('{}/{}/{}/Modify{}{}.java').format(self.configData['path_builder_plugins'], self.schemaName, self.actionsDir, self.schemaName.title(), ref)
            src = ('{}/ModifyTemplateSample.java').format(self.configData['path_builder_templates'])
            self.copyAndReplace(src,dst, form)


    def pathTemplateReplaceOut(self,templateType,formRef):

        fname = ('{}/{}/{}XDATScreen_{}').format(self.configData['path_builder_plugins'],self.schemaName,self.filesDir,templateType)
        return fname + ('_{}_{}.java').format(self.configData['schemaName'],formRef)
    

    def formEdit(self,form):


        templateName = self.loadTemplateReplace(form)
        writeFileName = self.pathTemplateReplaceOut('edit',form['ref'])

        self.log.append(' write file : {}'.format(writeFileName))
        self.checkDir(writeFileName)

        self.copyAndReplace(templateName,writeFileName, form)
