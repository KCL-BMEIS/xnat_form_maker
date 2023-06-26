import csv
import os
import sys
import time


class LoaderRedcap(object):


    #NOTES:
    # some are required BUT only if showing - ie, branched questions. So skip required if from branched
    

    def __init__(self, configData):

        self.errors = []
        self.log =[]
        self.configData = configData
        self.allowedFormTypes = ['text','dropdown','radio', 'multiradio', 'calc','tickbox','yn','ny','ynu','ynuo','textbox', 'textarea','date', 'header', 'subheader', 'paragraph', 'insertparagraph', 'datetime']
        self.allowedDataTypes = ['string', 'bool', 'float', 'int', 'header', 'complex', 'date', 'dateTime']
        self.allowedExtensions = ['subject', 'image', 'session']
        self.allowedDropDownTypes = ['int', 'string']
        self.toggle_panels = ['ynuo','yn','ny','ynu']
        self.textFormTypes =  ['header', 'subheader', 'paragraph', 'text']


    def hasError(self):
        return len(self.errors)

    def errors(self):
        return self.errors

    def dos2unix(self, path):
        #have to convert
        os.system("find ./redcap_dict/* -name *.csv -type f -exec dos2unix -u {} \; ")

    def filesList(self,path):
        out = []
        for file in os.listdir(path):
            if file.endswith('.csv') and '~' not in file:
                out.append(file)

        return out
        
    def loadRedcap(self,path,fileName):

        #schema name MUST be filename??
        # take as parmetrs?

        out = {'schema': '', 'order': [], 'forms': dict()}


        schemaName = fileName.replace(".csv", "").replace("_","").replace("-","")
        out['schema'] = schemaName
        out['restrict_to_project'] = ''


        data = dict()
        questions = dict()
        qs = []
        strId = ""

        fullPath = ('{}/{}' .format(path,fileName))



        #windows-1252?? convert beforehand

        with open(fullPath, mode='r', encoding='windows-1252') as redcap_csv:
            csv_reader = csv.DictReader(redcap_csv)
            print(f'Column names are ', csv_reader.fieldnames)
            line_count = 0
            prev_form_name = ""

            try:

                for row in csv_reader:

                    line_count += 1
                    #ignore images
                    if "img src" not in row["Field Label"]:

                        print('#########')
                        #print(row)
                        if row["Form Name"] != prev_form_name:
                            ## complete previous
                            if len(strId) > 0:
                                for q in qs:
                                    if 'branch_logic' in q:
                                        qs = self.cleanBranching(qs, q)
                                out['forms'][strId]['inputs'] = self.sortByDataName(qs)
                                qs = []

                            # The same.... ID and Name
                            prev_form_name =  row["Form Name"]
                            strId = row["Form Name"]
                            ## Bean can be tooo long
                            full_length = '{}{}'.format(schemaName, strId.replace("_"," "))
                            if len(full_length) > 68:
                                self.errors.append("Error reading rows: File {} Form {} is too long - {} chars. Replace Form Name in csv or shorten filename".format(schemaName, strId, len(full_length)))


                            formName = row["Form Name"].replace("_"," ").lower() # the form title
                            formRef = row["Form Name"].replace("_","").replace(' ', '').lower() # database name
                            ext = 'subject'
                            desc = row["Form Name"]

                            strId = strId.replace(' ', '')
                            data = dict()
                            data['strId'] = strId
                            data['name'] = formName.replace("'","").replace('-', '')
                            data['ref'] = formRef.replace(' ', '').replace("'","").replace('-', '').lower()

                            data['inputs'] = []
                            data['ext'] = ext.lower()
                            data['desc'] = desc
                            data['schema'] = schemaName

                            out['order'].append(strId)
                            out['forms'][strId] = data
                            print("Found form:{} -  {}".format(strId, out['forms'][strId]['name']))


                        ## read questions in
                        section_header = self.cleanCellValue(row["Section Header"]).replace('align:center;', 'align:left;')
                        # add paragraph for section_header - ignoring any images
                        if len(section_header) > 1:
                            questions = dict()
                            questions['parent'] = ''
                            questions['children'] = []
                            questions['schema'] = schemaName
                            questions['formRef'] = data['ref']

                            questions['question'] = section_header
                            questions['dataName'] = ''
                            questions['subName'] = ''
                            questions['inputFormType'] = 'paragraph'
                            questions['inputDataType'] = ''
                            questions['inputLen'] = 0
                            questions['required'] = '0'
                            questions['schemaInputType'] = 'text'
                            questions['hide'] = ''
                            qs.append(questions)

                        questions = dict()
                        questions['question']  = self.cleanCellValue(row["Field Label"]).replace('align:center;', 'align:left;')

                        questions['dataName'] = self.cleanCellValue(row["Variable / Field Name"]).replace("_","")
                        fieldType = self.cleanCellValue(row["Field Type"])
                        required = self.cleanCellValue(row["Required Field?"])
                        annotation= self.cleanCellValue(row["Field Annotation"])
                        #print(row["Choices, Calculations, OR Slider Labels"])

                        opts = self.cleanDropDownOptions(row["Choices, Calculations, OR Slider Labels"])
                        #print(opts)

                        questions['rawopts'] = row["Choices, Calculations, OR Slider Labels"]

                        questions['inputLenType'] = self.cleanCellValue(row["Text Validation Type OR Show Slider Number"])
                        inputLenMin = self.cleanCellValue(row["Text Validation Min"])
                        inputLenMax = self.cleanCellValue(row["Text Validation Max"])
                        questions['inputLen'] = 0
                        if inputLenMax != '':
                            if 'int' in questions['inputLenType']:
                                questions['inputLen'] = int(inputLenMax)
                            if 'numb' in questions['inputLenType']:
                                questions['inputLen'] = float(inputLenMax)
                        # IF date_dmy, or time then NOT text as shown in field type


                        questions['inputFormType'], questions['inputDataType'] = self.convertFieldType(fieldType, row["Choices, Calculations, OR Slider Labels"], questions['inputLenType'])


                        if 'multiradio' in questions['inputFormType']:
                            num = 1
                            for opt in opts.split(','):
                                print('test, option:',opt)
                                questions = dict()
                                questions['dataName'] = self.cleanCellValue(row["Variable / Field Name"]).replace("_","")
                                questions['inputDataType'] = 'boolean'
                                questions['inputFormType'] = 'tickbox'
                                questions['question']  = '{} - {}'.format(self.cleanCellValue(row["Field Label"]).replace('align:center;', 'align:left;'), opt)
                                questions['inputLen'] = 0
                                questions['required'] = '0'
                                questions['hide'] = ''
                                questions['options'] = ''

                                questions['parent'] = ''
                                questions['children'] = []
                                questions['schema'] = schemaName
                                questions['formRef'] = data['ref']
                                # does nto exist in redcap
                                questions['subName'] = num
                                questions['schemaInputType'] = self.schemaInputType(questions['inputFormType'], questions['inputDataType'])
                                num += 1

                                qs.append(questions)
                        else:

                            questions['parent'] = ''
                            questions['children'] = []
                            questions['schema'] = schemaName
                            questions['formRef'] = data['ref']
                            #does nto exist in redcap
                            questions['subName'] = ""

                            questions['required'] = '0'
                            #Skip if conditional required - ie, required if X is selected
                            if 'y' in required and not len(self.cleanCellValue(row["Branching Logic (Show field only if...)"])) > 0:
                                questions['required'] = '1'

                            questions['options']= opts
                            questions['hide'] = ''

                            if 'HIDE' in annotation:
                                questions['hide'] = 'x'
                            if 'DEFAULT' in annotation:
                                questions['default'] = annotation.replace('@DEFAULT','').replace('=','').replace('"','')
                                defaultopts = row["Choices, Calculations, OR Slider Labels"].split('|')
                                for op in defaultopts:
                                    if questions['default'] in op:
                                        op = op.translate({ord(c): "" for c in "!@#$%^&*()[]{};:./<>?\`~-=_+"})
                                        questions['default'] = " ".join(op.split()[1:])

                                print('Default found: {}'.format(questions['default']))
                                if 'aken' in defaultopts:
                                    sys.exit()

                            questions['schemaInputType'] = self.schemaInputType(questions['inputFormType'], questions['inputDataType'])
                            #other

                            if len(self.cleanCellValue(row["Branching Logic (Show field only if...)"])) > 0:
                                print('Only show if - found: ', row["Branching Logic (Show field only if...)"])
                                questions['branch_logic'] = row["Branching Logic (Show field only if...)"]


                            if len(self.cleanCellValue(row["Field Note"])) > 0:
                                questions['note'] = self.cleanCellValue(row["Field Note"])
                                questions['question'] = '{} ({})'.format(questions['question'], questions['note'])

                            qs.append(questions)

                        if not questions['question']:
                            print('No question found! form name:{}      section_header:{}'.format(row["Form Name"], section_header))
                            continue


                #in case there is no extra line, then skips...
                if len(qs) > 0:
                    for q in qs:
                        if 'branch_logic' in q:
                            qs = self.cleanBranching(qs, q)
                    out['forms'][strId]['inputs'] = self.sortByDataName(qs)
                    qs = []
            except Exception as e:
                self.errors.append("Error - last form {} line {} {} - reading rows: {}".format(prev_form_name,line_count,questions['question'],e))
                print(self.errors())
                sys.exit(0)


        for x in out['forms']:
            self.checkForm(out['forms'][x])

        return out



    def checkInput(self,formName,i):

        # check form type
        if i['inputFormType'] not in self.allowedFormTypes :
            self.errors.append('Form {} Question : {} ,Invalid Form Type {} '.format(formName, i['question'],i['inputFormType']))

        # check data type
        if (i['inputDataType'] != '') and (i['inputDataType'] not in self.allowedDataTypes) :
            self.errors.append('Form {} Question : {} ,Invalid Data Type {} '.format(formName, i['question'],i['inputDataType']))


    def convertFieldType(self, fieldType, opts, lenType):

        #Lentype Has to come first, as string in redcap
        if 'datetime' in lenType:
            return 'datetime','string'
        elif 'date' in lenType:
            return 'date','date'
        elif 'time' in lenType:
            return 'time','string'
        elif 'number' in lenType:
            return 'textbox','float'
        elif 'integer' in lenType:
            return 'textbox','integer'

        if 'text' in fieldType:
            return 'textbox','string'
        if 'calc' in fieldType:
            #datediff and sums...
            if 'if(' in opts and 'datediff' in opts:
                # just do text box for now
                return 'calcifdd', 'string'
            if 'if(' in opts and 'sum' in opts:
                # just do text box for now
                return 'calcifsum', 'string'
            if 'if(' in opts:
                # just do text box for now
                return 'calcif', 'string'
            elif 'datediff' in opts:
                return 'calcdd', 'float'
            elif 'sum' in opts:
                return 'calcsum', 'float' # need to make hidden in edit form. Usually date difference
            else:
                #just do text box for now
                return 'calc', 'string'
        if 'yesno' in fieldType or 'truefalse' in fieldType:
            return 'tickbox', 'boolean'
        if 'notes' in fieldType:
            return 'textarea', 'string'
        if 'radio' in fieldType:
            return 'radio', 'string'
        if 'descriptive' in fieldType:
            return 'paragraph', ''
        if 'dropdown' in fieldType:
            return 'dropdown', 'string'
        if 'checkbox' in fieldType:
            return 'multiradio', 'string'


    def schemaInputType(self,formType,dataType):
        iType='none'
        if formType.lower() in self.textFormTypes:
            iType = 'text'
            return iType
        else:
            iType = 'string' if not dataType else dataType


        if 'ool' in dataType:
             iType='boolean'

        elif 'int' in dataType:
            iType='integer'
        elif 'loat' in dataType:
            iType='float'

        elif formType == 'date':
            iType = 'date'
        elif formType == 'datetime':
            iType = 'string'
        if formType.lower() in self.textFormTypes:
            iType == 'text'
        if formType == 'dropdown' and not dataType:
            #only assumes int if specifies int
            iType = 'string'

        if 'tickbox' in formType:
            iType='boolean'

        return iType

    def setLength(self,data):
        if not data:
            return 0
        else:
            try:
                return int(data)
            except Exception as e:
                print("not an int - {} -  floats not restictable? {}".format(data))
                return ''

    def cleanBranching(self, qs, question ):

        ## example: in 'Branching Logic (Show field only if...)
        #      [c_section] = '1'    - NOT in order, can be anywhere. Also can be muitple OR or refer from another form
        #   panel name:   [original question - dataname][panel num]
        # generic macro - fmGenericStringToggle $name $item $items $default $panel $vals $vr)
        # for each value, numbers it. Then on each click has a panel.
        # issue  -it appears not in order - the original question can be after

        # only do if simple - so only one

        condition = question['branch_logic']
        if len(condition.split('=')) == 2:
            a = condition.split('=')
            #val = self.cleanDropDownOptions(a[1])#.replace("'","").replace('"','').replace(" ","")
            val = a[1].replace("'","").replace('"','').replace(" ","")


            # excludes referencs to other forms
            if len(a[0].split(']')) == 2:
                #el is branching question
                el = a[0].replace('[','').replace(']','').replace('_','').replace(" ","")
                print(a, val,el)
                if ')' not in el:
                    for q in qs:
                        #print(q['dataName'])
                        if q['dataName'] == el:
                            print("CLEAN BRANCHING: FOUND EL {}  question: {}  val: -{}-  schme type: {}".format(el, q['dataName'], val, q['schemaInputType']))
                            if 'ool' in q['schemaInputType']:
                                val = val.replace(" ","")
                                print("FOUND BOOLEAN val {}".format(val))
                                #ynredcap - can open both if 0 or 1
                                q['inputFormType'] = 'ynredcap'
                                if 'branchNum' in q:
                                    print(q['branchNum'])
                                    q['branchNum'] += 1
                                else:
                                    q['branchNum'] = 1
                                    
                                if 'branchVals' not in q:
                                    q['branchVals'] =''
                                if '0' in val:
                                    question['panelNum'] = '{}'.format(q['branchNum'])
                                    q['branchVals'] = '{}{}'.format(q['branchVals'], 'N')
                                else:
                                    question['panelNum'] = '{}'.format(q['branchNum'])
                                    q['branchVals'] = '{}{}'.format(q['branchVals'], 'Y')

                            elif 'rawopts' in q:
                                for option in q['rawopts'].split('|'):

                                    if '{},'.format(val) in option:
                                        if 'branchVals' not in q:
                                            q['branchVals'] = []
                                        # remove the option number (format, example '1, yes')
                                        val = " ".join(option.split()[1:]).replace(',','')
                                        print("FOUND conditional_val: {}  option: {}".format(val, option))
                                        q['branchVals'].append(val.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:./<>?\`~-=_+"}))
                                        if 'branchNum' in q:
                                            print(q['branchNum'])
                                            q['branchNum'] += 1
                                        else:
                                            q['branchNum'] = 1

                                        question['panelNum'] = q['branchNum']


                    el = '{}:{}/{}'.format(question['schema'], question['formRef'], el)

                    question['branchingquestion'] = el
                    question['branchingvalue'] = val.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:./<>?\`~-=_+"})
                    if 'branchNum' in q:
                        print("BRANCHING CLEANING: bracnch found in: {} element  {}  PanelNUm: {}  value {} ".format(question['dataName'], el,question['branchNum'], question['branchingvalue']))
                    #time.sleep(2)
                    ## if redoing, then replace existing:
                    for q in qs:
                        if q['dataName'] == question['dataName']:
                            q['branchingquestion'] = question['branchingquestion']
                            if 'panelNum' in q:
                                print('panel num:',question['panelNum'])
                                q['panelNum'] = question['panelNum']
                            q['branchingvalue'] = question['branchingvalue']

        return qs





    def cleanCellValue(self,data):

        if (not data or data == None):
            
            return ''
        data = data.strip().encode('ascii', 'ignore')
        data_str=data.decode()

        return data_str

        # return '' if not data else data.strip()

    def cleanDropDownOptions(self,o):

        # in redcap split by | - need to replace with ,
        bstr= '{}'.format(o)
        # have to replace as | sepreated, and need to change to  comma seperated
        bstr = bstr.replace(",", " ")

        bstr = bstr.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:./<>?\`~-=_+"})

        cstr = ''
        first=True
        for i in bstr.split('|'):
            if first:
                cstr = " ".join(i.split()[1:])
                #print('test opts in redcap: 1st:', i, '  cstr:', cstr)
                first = False
                #sys.exit(0)
            else:
                cstr = '{},{}'.format(cstr, " ".join(i.split()[1:]))
        #cstr = cstr[2:]

        return cstr

    def sortByDataName(self,inputs):

        temp = {'order': [], 'inputs' : {}}
        out = []
        #urgh, fix to stop recounting repeated paragraphs/headers
        textnum = 555
        for i in inputs:
            
            dataName = i['dataName']
            if i['inputFormType'] in self.textFormTypes:
                dataName = str(textnum)
                textnum = textnum + 1

            if dataName in temp['inputs'].keys():
                i['parent'] = dataName
                temp['inputs'][dataName]['children'].append(i)
            else:
                temp['inputs'][dataName] = i 
                temp['order'].append(dataName)
                # out[i['dataName']] = [i]

        for o in temp['order']:
            out.append(temp['inputs'][o])
        #print('------------###########-----------')
        #print('{}'.format(out))
        #print temp['order']
        return out

    #TODO needs update
    def checkForm(self,form):
            


       
        if form['ext'] not in self.allowedExtensions :
            self.errors.append('Form {} Invalid Extension {} '.format(form['name'], form['ext']))
        # already checked if no inputs
        # reset list for questions
        qs = []

        for i in form['inputs']:
            print('CHECKDATA: {}'.format(i))
            # yn do not NEED subnames as already exist. (completed, reasonnotable)
            #if 'yn' in i['inputFormType'] and len(i['subName'])<1:
            #    self.errors.append('Form {} has missing subname: {} - {} - {}'.format(form['name'], i['question'],i['dataName'], i['inputFormType']))


            temp = i['question'].replace(" ",'') + i['dataName']
            if temp in qs and i['inputFormType'] not in self.textFormTypes:
                self.errors.append('Form {} has Dupe input {} - {}'.format(form['name'], i['question'],i['dataName']))
            else:
                qs.append(temp)
            # not for redcap, not doing subtypes
            #if len(i['children']) < 1 and  i['inputFormType'] in self.toggle_panels:
            #    self.errors.append('Form {}: Question: {} - Panel Toggle Type {} has no subtypes! '.format(form['name'], i['question'],i['dataName']))


            #TODO check for group inputs with no subname

    def printForms(self,forms):
       
        # already checked if no inputs
        for f in forms:
            print('Form {}'.format(forms[f]['name']))
            print('schema {}'.format(forms[f]['schema']))

            for i in forms[f]['inputs']:
                print(' -- input : question {}  : Type {}'.format(i['question'], i['inputFormType']))
                if len(i['children']) > 0:
                    for c in i['children']:
                        print('    -- input : question {} : Type {}'.format(c['question'],c['inputFormType']))


