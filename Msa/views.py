import pandas as pd
from pandas import DataFrame, ExcelWriter
from zipfile import ZipFile
import json
from django.shortcuts import render
from django.views import View  
from django.core.files.storage import FileSystemStorage

def ReadLog(_log):
    df_common = {}
    df_result = {}
    d_uper = {}
    d_lower = {}
    for x in _log:
        x= x.replace('"','')
        row = x.split(',')
        row.pop()
        if len(row)>5 and row[0]!='STEP':
            row[0] = int(row[0])
            if row[5]=='':
                row[5]=row[6]
            row[7] = int(row[7].replace('%',''))
            row[8] = int(row[8].replace('%',''))
            row[12] = int(row[12])
            row[13] = int(row[13])
            row[14] = int(row[14])
            row[15] = int(row[15])
            row[16] = int(row[16])
            row[17] = int(row[17])
            row[18] = int(row[18])
            if row[19]!="":
                row[19] = float(row[19])
            else:
                row[19] = 0
            row.pop(3)
            row.pop(2)
            row.pop(-2)
            row[4] = ''.join(c for c in row[4] if c.isalpha())
            if row[4]=='':row[4]='O'
            row[3] = ''.join(c for c in row[3] if c.isdigit() or c=='.')
            if row[3]!='':
                row[3] = float(row[3])  
                row[5] = round(row[3]+(0.01*row[3]*row[5]),4)
                row[6] = round(row[3]-(0.01*row[3]*row[6]),4)
            if row[18]=='Skip': row[17]= '-'

            df_common["Step"+" "+ str(row[0])] = [row[2],row[1],row[10],row[11],row[3],row[4]]
            df_result["Step"+" "+ str(row[0])] = [row[17]]
            d_uper["Step"+" "+ str(row[0])] = [row[5]]
            d_lower["Step"+" "+ str(row[0])] = [row[6]]

    dfCommon = DataFrame.from_dict(df_common)
    dfResult = DataFrame.from_dict(df_result)
    dfUpspec = DataFrame.from_dict(d_uper)
    dfLowSpec = DataFrame.from_dict(d_lower)
    return dfCommon,dfResult,dfUpspec,dfLowSpec

def readZip(zip_file):
    dfCommon = []
    dfResult = []
    dfUpspec = []
    dfLowSpec = []
    i=0
    with ZipFile(zip_file) as zf:
            for file in zf.namelist():
                if not file.endswith('.csv'): # optional filtering by filetype
                    continue
                with zf.open(file) as f:
                    textfile = f.read().decode('utf-8')
                    a = textfile.split('\r\n')
                    df_common,df_result,df_upspec,df_lowspec = ReadLog(a)
                    df_result.index = [i +1]
                    if i==0:
                        df_common.index = ['Part','Board','A','B','Standard','Unit']
                        df_upspec.index = ['Upper Spec']
                        df_lowspec.index = ['Lower Spec']
                        dfCommon = df_common
                        dfResult = df_result
                        dfUpspec = df_upspec                
                        dfLowSpec = df_lowspec
                        i=i+1
                    else:
                        dfResult = pd.concat([dfResult, df_result], axis=0)
                        i=i+1
    df_subcrible = dfResult.describe().iloc[[0,1,2,3,7]].round(4)
    # print(df_subcrible)
    df_report = pd.concat([dfCommon,dfUpspec,dfLowSpec,df_subcrible]).transpose()
    df_report['Cpl'] = (df_report['mean']-df_report['Lower Spec'])/(3*df_report['std']+0.0001)
    df_report['Cpu'] = (df_report['Upper Spec']-df_report['mean'])/(3*df_report['std']+0.0001)
    df_report['Cpk'] = df_report[['Cpl','Cpu']].min(axis=1)
    df_report = df_report.round(4)
    df_report = df_report.drop(['Cpl', 'Cpu'], axis=1)
    # dfAll  = pd.concat([df_report.transpose(),dfResult])
    return df_report.transpose(),dfResult

class MsaView(View):
    def get(self, request):
        return render(request, 'Msa/index.html')
    
    def post(self,request):
        myfile = request.FILES['myfile']
        dfReport, dfResult = readZip(myfile)
        dfAll =  pd.concat([dfReport,dfResult])

        columns = dfReport.transpose().columns.tolist()
        report =  dfReport.transpose().values.tolist()
        # print(data)
      
        context = {'cot':columns,'report': report}      
        return render(request, 'Msa/result.html',context)