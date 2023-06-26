import os
import shutil




class CSVHandler(object):

    def __init__(self, configData, deleteExistingFiles=False):
        self.errors = []
        self.log = []
        self.configData = configData
        self.schemaName = configData['schemaName']
        self.csvDir = '{}/data'.format(configData['path_plugin_builder'])


        if (deleteExistingFiles):
            self.emptyTheDir()

    def hasError(self):
        return len(self.errors)

    def errors(self):
        return self.errors




    def emptyTheDir(self):

        thePath = ('{}/data/{}').format(self.configData['path_plugin_builder'], self.schemaName)
        if os.path.exists(thePath):
            self.log.append(' Delete Dir : {}'.format(thePath))
            shutil.rmtree(thePath)
        #make new dir

        os.makedirs(thePath)


    def getHeader(self, form):

        out = 'ID,'
        for i in form['inputs']:
            el = '{}:{}/{}'.format(self.schemaName, form['ref'], i['dataName'])
            if 'subform' in i['inputFormType']:

                subform = i['options']
                #insert questions later
                out = '{}{}@{}@,'.format(out, el,subform)

            elif len(i['children']) > 0:
                elsub = '{}/{}'.format(el, i['subName'])
                out = '{}{},'.format(out, elsub)
                for ii in i['children']:
                    elsub = '{}/{}'.format(el, ii['subName'])
                    if 'subform' in ii['inputFormType']:
                        subform = ii['options']
                        # insert questions later
                        out = '{}{}@{}@,'.format(out, elsub, subform)
            else:
                out = '{}{},'.format(out, el)
        out = '{}subject_ID'.format(out )
        return out

    def getLineOfData(self, form, data):


        form_label = '{}-{}'.format(form['ref'],data['subject_label'])
        out = '{},'.format(form_label)

        for i in data['inputs']:
            out = '{},{},'.format(out, data[i])
        out = '{},{}'.format(out, data['subject_label'] )
        return out

    def writeToFile(self, form):

        head = self.getHeader(form)

        if len(head) == 0:
            self.errors.append('no inputs')
            return

        writeFileName = '{}/{}/{}_{}.csv'.format(self.csvDir,self.schemaName,self.schemaName, form['ref'])
        #self.checkDir(writeFileName)
        self.log.append(' write file : {}'.format(writeFileName))
        f = open(writeFileName, "w")

        f.write('{}'.format(head))

        f.close()

    def write_subforms(self, subform):
        thePath = ('{}/data/{}').format(self.configData['path_plugin_builder'], self.schemaName)
        subform_replace = '@{}@'.format(subform['ref'])
        out = ''
        if os.path.exists(thePath):
            for filename in os.listdir(thePath):
                filepath = os.path.join(thePath, filename)
                with open(filepath) as f:
                    header = f.readline()
                    heads = header.split(',')
                    for head in heads:
                        print(head)
                        if subform_replace in head:
                            el = head.replace(subform_replace,'')
                            print(el)
                            for i in subform['inputs']:
                                out = '{},{}/{}'.format(out,el, i['dataName'])

                        else:
                            out = '{},{}'.format(out,head)

                with open(filepath, "w") as f:
                    #get rid of first and last comma
                    out = out[1:-1]
                    f.write(out)

