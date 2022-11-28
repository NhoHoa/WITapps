from django.shortcuts import render
from django.views import View
import csv, io
import pandas as pd
def findSpece(row):
	i=0
	for x in row:
		if(x==''):
			i = i+1
		else:
			i=0
	return i
	
def read_log(myfile):
    file = myfile.read().decode("utf-8")
    csv_reader = file.split("\r\n")
    column = []
    data=[]
    for line in csv_reader:
        row = line.split(',')
        if  len(row) > 8:

            if findSpece(row)<40:
                if row[0]=='Judgment result':
                    column = row
                elif row[0]=='':
                    pass
                else:
                    print(row)
                    if row[8]!='-':
                        data.append(row)

    df = pd.DataFrame(data,columns =column)	
    df = df[['Layout No.','Volume', 'Height', 'Area', 'X shift', 'Y shift']]

    df['Layout No.'] = df['Layout No.']
    df['Volume'] = pd.to_numeric(df['Volume'])
    df['Height'] = pd.to_numeric(df['Height'])
    df['Area'] = pd.to_numeric(df['Area'])
    df['X shift'] = pd.to_numeric(df['X shift'])
    df['Y shift'] = pd.to_numeric(df['Y shift'])
    d_spec = {'Volume': [75, 170], 
        'Height': [75, 170],
        'Area': [75, 170],
        'X shift': [-25, 25],
        'Y shift': [-25, 25],
        }
    df_spec = pd.DataFrame(data=d_spec,index=['lower', 'upper'])
    df_all = pd.concat([df_spec, df.describe().iloc[[0,1,2,3,7]].round(4)], axis=0)
    df_report  = df_all.transpose()
    df_report['Cpl'] = (df_report['mean']-df_report['lower'])/(3*df_report['std']+0.0001)
    df_report['Cpu'] = (df_report['upper']-df_report['mean'])/(3*df_report['std']+0.0001)
    df_report['Cpk'] = df_report[['Cpl','Cpu']].min(axis=1)
    df_all = pd.concat([df,df_report.transpose()], axis=0)
    return df_all

class AsangView(View):
    def get(self, request):
        return render(request, 'asang/index.html')
    
    def post(self,request):
        myfile = request.FILES['myfile']
        # file = myfile.read().decode('utf-8')
        # print(file)
        dfAll = read_log(myfile)
      
        # dfAll = dfAll.transpose()

        columns = dfAll.columns.tolist()
        report =  dfAll.values.tolist()
        # # print(data)
      
        context = {'cot':columns,'report': report}      
        return render(request, 'asang/result.html',context)