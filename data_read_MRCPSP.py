#Author:Zhao fei
import re
import  pandas as pd

def dataRead(file):
    with open(file) as f:
        data = f.readlines()
    data = [x.strip() for x in data]
    data = [re.split(r' +', x) for x in data]
    return data

def dataStore(ins,file):
    data=dataRead(file)

    ins.number_job = int(data[5][4])
    ins.number_renewable_resources =int(data[8][3])
    ins.number_unrenewable_resources = int(data[9][3])
    ins.resource_capacity=[int(i) for i in data[85]]     # 14:85
    # print(ins.resource_capacity)

    #successor
    for job in range(18,18+ins.number_job):
        ins.job_num_successors.append(int(data[job][2]))
        ins.job_successors.append([int(i) for i in data[job][3:]])
    #predecessors
    for _ in range(ins.number_job):
        ins.job_predecessors.append([])
    for job in range(ins.number_job):
        for successor in ins.job_successors[job]:
            ins.job_predecessors[successor-1].append(job+1)
    #duration and resources
    Row = 39    #14:39
    for job in range(2,ins.number_job):
        resource={}
        duration={}
        for model in range(3):
            if model==0:
                duration[model+1]=int(data[Row+model][2])
                ins.job_model_duration[job]=duration

                resource[model+1]=[int(res) for res in data[Row+model][3:]]
                ins.job_model_resource[job]=resource
            else:
                duration[model + 1] = int(data[Row + model][1])
                ins.job_model_duration[job] = duration

                resource[model + 1] = [int(res) for res in data[Row + model][2:]]
                ins.job_model_resource[job] = resource
        Row+=3



def read_CNfks(ins,path):
    data_xls = pd.ExcelFile(path)

    data={}
    for name in data_xls.sheet_names:
        df=data_xls.parse(sheetname=name,header=None)
        df.index = ["f" + str(i + 1) for i in range(6)]
        df.columns = ["k1", "k2", "k3"]
        data[name]=df
    ins.CNfks=data

def read_Ofs(ins,file):
    column = ["s" + str(i + 1) for i in range(7)]
    index = ["f" + str(i + 1) for i in range(6)]
    a = pd.read_excel(file, header=None)
    a.index = index
    a.columns = column
    ins.Ofs=a

def read_qfs(ins,file):
    column = ["s" + str(i + 1) for i in range(7)]
    index = ["f" + str(i + 1) for i in range(6)]
    a = pd.read_excel(file, header=None)
    a.index = index
    a.columns = column
    ins.qfs=a
