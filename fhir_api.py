import urllib
from urllib import parse
import requests

fhir_patient = 'http://fhirtest.uhn.ca/baseDstu3/Patient?'
fhir_condition = 'http://fhirtest.uhn.ca/baseDstu3/Condition?'


class FHIRQueryByID:
    def __init__(self, id):
        self.id = id
        self.setPatientID()

    def setPatientID(self):
        url_patient = fhir_patient + urllib.parse.urlencode({'_id': self.id})
        url_condition = fhir_condition + urllib.parse.urlencode({'patient': self.id})
        self.json_data_patient = requests.get(url_patient).json()
        self.json_data_condition = requests.get(url_condition).json()
        self.resource_patient = self.json_data_patient['entry'][0]['resource']
        self.resource_condition = self.json_data_condition['entry']

    def getResourceType(self):
        resource_type_patient = self.resource_patient['resourceType']
        resource_type_condition = self.resource_condition['resourceType']
        return resource_type_patient, resource_type_condition

    def getName(self):
        name_data = self.resource_patient['name'][0]['text']
        return name_data

    def getBirthDate(self):
        birth_date = self.resource_patient['birthDate']
        return birth_date

    def getGender(self):
        gender = self.resource_patient['gender']
        return gender

    def getPatientURL(self):
        patient_url = self.json_data_patient['entry'][0]['fullUrl']
        return patient_url

    def getAdminData(self):
        # print('Resource Type: ' + self.getResourceType()[0])
        print(self.getPatientURL())
        print(self.getName())
        print(self.getBirthDate())
        print(self.getGender())

    def getConditionData(self):
        n = 0
        diagnoses = []
        for item in self.resource_condition:
            diagnosis_item = str(self.resource_condition[n]['resource']['code']['coding'][0]['display'])
            diagnosis_severity = str(self.resource_condition[n]['resource']['severity']['text'])
            diagnosis = 'Diagnosis: ' + diagnosis_item + " , " + 'Severity: ' + diagnosis_severity
            n += 1
            diagnoses.append(diagnosis)

        return diagnoses

    def getPatientCondition(self):
        for item in self.getConditionData():
            print(str(item))


x = FHIRQueryByID('157002')
print('-------Patient admin data--------')
x.getAdminData()
print('-------Condition--------')
x.getPatientCondition()
