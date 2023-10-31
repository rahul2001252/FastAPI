import requests
import xmltodict
import json
import copy

class JsonToRecord:
    def __init__(self, rec_type):
        self.records = {}
        self.type = rec_type

    def show(self):
        for k, v in self.records.items():
            print("Record Type {} count {}\n".format(k, len(v)))
            for li in v:
                print("  Record : {} \n".format(li))


    def clear(self):
        self.records = {}
 

    def make_key(self, prefix, attribute):
        if prefix.lower() not in attribute.lower():
            return prefix + attribute
        else:
            return attribute
 
    def add_record(self, rec_type, record):
        if rec_type in self.records:
            self.records[rec_type].append(record)
        else:
            self.records.update( {rec_type : [ record ] })
 
    def process_description(self, d, record):
        print("process description called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            temp_key = self.make_key("desc", k)
            new_record.update({ temp_key : v })
 
    def process_dataitem(self, d, record):
        print("process dataitem called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            temp_key = self.make_key("dataItem", k)
            new_record.update({ temp_key : v })
 
        self.add_record("DataItem", new_record)
        return copy.deepcopy(new_record)
 
    def process_dataitems(self, d,  record):
        print("process dataitems called")
        if isinstance(d, list):
            for li in d:
                self.process_dataitem(li, record)
        else:
            nonlistvalues = 0
            if isinstance(d, dict) :
               for k, v in d.items():
                   if k == "DataItem" and isinstance(v, list):
                       self.process_dataitems(v, record)
                   else:
                       nonlistvalues = nonlistvalues +  1
            else:
                nonlistvalues = nonlistvalues +  1
 
            if nonlistvalues > 0:
                self.process_dataitem(d, record)

    def process_event(self, d,  record):
        print("process event called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            new_record.update({ "event" : k })
            self.process_dataitems(v, new_record)
        return copy.deepcopy(new_record)
 
    def process_events(self, d,  record):
        print("process events called")
        if isinstance(d, list):
            for li in d:
                self.process_event(li, record)
        else:
            self.process_event(d, record)
 
    def process_condition(self, d,  record):
        print("process condition called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            new_record.update({ "condition" : k })
            self.process_dataitems(v, new_record)
        return copy.deepcopy(new_record)
 
    def process_conditions(self, d,  record):
        print("process conditions called")
        if isinstance(d, list):
            for li in d:
                self.process_condition(li, record)
        else:
            self.process_condition(d, record)
 
    def process_sample(self, d,  record):
        print("process sample called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            new_record.update({ "sample" : k })
            self.process_dataitems(v, new_record)
        return copy.deepcopy(new_record)
 
    def process_samples(self, d,  record):
        print("process samples called")
        if isinstance(d, list):
            for li in d:
                self.process_sample(li, record)
        else:
            self.process_sample(d, record)
 
    def process_header(self, d, record):
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            temp_key = self.make_key("header", k)
            new_record.update({ temp_key : v })
 
        self.add_record("Header", new_record)
        return copy.deepcopy(new_record)
 

#########  Stream Document

class SampleJsonToRecord(JsonToRecord):
    def __init__(self, rec_type):
        super().__init__(rec_type)
 
    def process_component(self, d,  record):
        print("process component called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, dict):
                if k == "Events":
                    self.process_events(v, new_record)
                elif k == "Condition":
                    self.process_conditions(v, new_record)
                elif k == "Samples":
                    self.process_samples(v, new_record)
                else:
                    print("Ignored key {} data in component".format(k))
            else:
                temp_key = self.make_key("component", k)
                new_record.update({ temp_key : v })
 
        self.add_record("DeviceComponent", new_record)
        return copy.deepcopy(new_record)
 
    def process_components(self, d,  record):
        print("process components called")
        if isinstance(d, list):
            for li in d:
                self.process_component(li, record)
        else:
            self.process_component(d, record)
 
    def process_device(self, d,  record):
        print("process device called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, list) or isinstance(v, dict) :
                if k == "ComponentStream":
                    self.process_components(v, new_record)
                else:
                    print("Ignored key {} data in device".format(k))
            else:
                temp_key = self.make_key("device", k)
                new_record.update({ temp_key : v })
 
        self.add_record("Device", new_record)
        return copy.deepcopy(new_record)
 
    def process_devices(self, d,  record):
        print("process devices called")
        if isinstance(d, list):
            for li in d:
                self.process_device(li, record)
        else:
            self.process_device(d, record)
 
    def process_stream(self, d,  record):
        print("process stream called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, dict):
                if k == "DeviceStream":
                    self.process_devices(v, new_record)
                else:
                    print("Ignored key {} data in streams".format(k))
            else:
                temp_key = self.make_key("device", k)
                new_record.update({ temp_key : v })
 
    def process_streams(self, d,  record):
        print("process streams called")
        if isinstance(d, list):
            for li in d:
                self.process_stream(li, record)
        else:
            self.process_stream(d, record)
 
    def process_mtconnect(self, d,  record):
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, dict):
                if k == "Header":
                    self.process_header(v, new_record)
                elif k == "Streams":
                    self.process_streams(v, new_record)
                else:
                    print("Ignored key {} data in mtconnect".format(k))
            else:
                temp_key = self.make_key("mtconnect", k)
                new_record.update({ temp_key : v })
 
    def process_document(self, d,  record = {}):
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, dict):
                if k == "MTConnectStreams":
                    self.process_mtconnect(v, new_record)
                else:
                    print("Ignored key {} data in document".format(k))
            else:
                temp_key = self.make_key("document", k)
                new_record.update({ temp_key : v })
 
 
 
#########  Device Document
class DeviceJsonToRecord(JsonToRecord):
    def __init__(self, rec_type):
        super().__init__(rec_type)
 
    def process_component(self, d,  record, sub = ""):
        print("process component called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            new_record.update({ sub + "Component" : k })
            if isinstance(v, dict):
                if k == "Components":
                    self.process_components(v, new_record, sub + "Sub")
                elif k == "DataItems":
                    self.process_dataitems(v, new_record)
                else:
                    print("Ignored key {} data in component".format(k))
            elif isinstance(v, list):
                self.process_components(v, new_record, sub)
            else:
                temp_key = self.make_key("Component", k)
                new_record.update({ temp_key : v })
 
        self.add_record("Component", new_record)
        return copy.deepcopy(new_record)
 
    def process_components(self, d,  record, sub = ""):
        print("process components called")
        if isinstance(d, list):
            for li in d:
                self.process_component(li, record)
        else:
            self.process_component(d, record)
 
    def process_device(self, d,  record):
        print("process device called")
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, dict) :
                if k == "Description":
                    self.process_description(v, new_record)
                elif k == "DataItems":
                    self.process_dataitems(v, new_record)
                elif k == "Components":
                    self.process_components(v, new_record)
                else:
                    print("Ignored key {} data in device".format(k))
            else:
                temp_key = self.make_key("device", k)
                new_record.update({ temp_key : v })
 
        self.add_record("Device", new_record)
        return copy.deepcopy(new_record)
 
    def process_devices(self, d,  record):
        print("process devices called")
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "Device":
                    self.process_devices(v, record)
        elif isinstance(d, list):
            for li in d:
                self.process_device(li, record)
        else:
            self.process_device(d, record)
 
 
    def process_mtconnect(self, d,  record):
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, dict):
                if k == "Header":
                    self.process_header(v, new_record)
                elif k == "Devices":
                    self.process_devices(v, new_record)
                else:
                    print("Ignored key {} data in mtconnect".format(k))
            else:
                temp_key = self.make_key("mtconnect", k)
                new_record.update({ temp_key : v })
 
    def process_document(self, d,  record = {}):
        new_record = copy.deepcopy(record)
        for k, v in d.items():
            if isinstance(v, dict):
                if k == "MTConnectDevices":
                    self.process_mtconnect(v, new_record)
                else:
                    print("Ignored key {} data in document".format(k))
            else:
                temp_key = self.make_key("document", k)
                new_record.update({ temp_key : v })
 
 
#url = https://smstestbed.nist.gov/vds/probe
#url = https://smstestbed.nist.gov/vds/Mazak01/probe
url = "https://smstestbed.nist.gov/vds/Mazak01/current"
#url = https://smstestbed.nist.gov/vds/Mazak01/sample
 
response = requests.get(url)
print(response)
#print(response.content)
xml_data = response.content

# Parse the XML data into a dictionary
xml_dict = xmltodict.parse(xml_data)
print(xml_dict)

# Convert the dictionary to a JSON string
json_str = json.dumps(xml_dict, indent=4)
print(json_str)
 

srecord = SampleJsonToRecord("SampleDoc")

srecord.process_document(xml_dict)
srecord.show()

#drecord = DeviceJsonToRecord("DeviceDoc")
#drecord.process_document(xml_dict)
#drecord.show()

 