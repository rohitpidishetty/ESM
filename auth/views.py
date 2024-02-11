from django.shortcuts import render, HttpResponse, redirect

# Create your views here.
import pandas as pd
import numpy as np

class SED:
  SETTINGS = {
    '0' : '20ae1f',
    '1' : '01ed4afc',
    '2' : '5ae9d77',
    '3' : '70ed93ff',
    '4' : '0000ed3fe',
    '5' : '6edf7bb',
    '6' : 'b45ccea',
    '7' : 'affed54c',
    '8' : '985aeddcdf30d',
    '9' : '1ed2ff0e300',
    '-1' : 'NULL'
  }
  rSETTINGS = {
    '20ae1f' : '0',
    '01ed4afc' : '1',
    '5ae9d77' : '2',
    '70ed93ff' : '3',
    '0000ed3fe' : '4',
    '6edf7bb' : '5',
    'b45ccea' : '6',
    'affed54c' : '7',
    '985aeddcdf30d' : '8',
    '1ed2ff0e300' : '9',
    'NULL' : 'NEGATIVE'
  }
  eSettings = {
    '0' : 'b',
    '1' : 'e',
    '2' : 'c',
    '3' : 'a',
    '4' : 'f',
    '5' : 'y',
    '6' : 'h',
    '7' : 'k',
    '8' : 'n',
    '9' : 'w'
  }
  reSettings = {
    'b': '0',
    'e': '1',
    'c': '2',
    'a': '3',
    'f': '4',
    'y': '5',
    'h': '6',
    'k': '7',
    'n': '8',
    'w': '9'
  }
  def encrypt(self, id):
    try:
      return "".join([((self.SETTINGS[str(id[i])] if str(id[i]) in list(self.SETTINGS.keys()) else self.SETTINGS["-1"]) + ("x" if i != len(id) - 1 else "") ) for i in range(len(id))])
    except Exception as e:
      return redirect('/UNF-404-ERR')
  
  def decrypt(self, id):
    try:
      return "".join([(self.rSETTINGS[str(i)] if str(i) in list(self.rSETTINGS.keys()) else self.rSETTINGS["3ffe"]) for i in str(id).split('x')])
    except Exception as e:
      return 'NULL'
    
  def encode(self, id):
    return "".join([self.eSettings[str(id[i])] for i in range(len(id))])
   
  def decode(self, id):
    return "".join([self.reSettings[str(id[i])] for i in range(len(id))])


class EmployeeScheduleManager:
  DAYS = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
  def __init__(self, data) -> None:
    self.data = data
    self.data['EMP_ID'] = self.data['EMP_ID'].astype('str')
 
  def getEmployees(self) -> list:
    self.employees = [employee for employee in list(self.data["EMP_ID"]) if employee != 'NAN']
    return self.employees
  
  def index(self, id):
    for i in range(len(self.employees)):
      if self.employees[i] == id:
        return i + 1
      if i == len(self.employees) - 1:
        return 0
    return -1 
  
  def calculateHours(self, object) -> dict:
    if(len(object) == 3):
      start = object[0].split(":")
      end = object[1].split(":")
      object[0] = float(start[0]) + float(int(start[1]) / 60)  if(len(start) == 2) else float(start[0])
      object[1] = float(end[0]) + float(int(end[1]) / 60)  if(len(end) == 2) else float(end[0])
      return {object[2] : {'HOURS' : (object[1] - object[0]), 'TIME' : f'{object[0]} to {object[1]}'}}, (object[1] - object[0])
    return 0.0
        
  def fetch(self, id) -> dict:
    df = pd.DataFrame(self.data)
    data = df.iloc[self.index(id)]
    schedule = []
    for day in self.DAYS:
      time = data[day]
      time = time.replace('CL', '23' if day in self.DAYS[:5] else '21')
      stamp = str(time).split('-')
      stamp = [(T.replace('AM', '').replace('PM', '')) for T in stamp]
      schedule.append(stamp + [day])
    TotalHours = 0
    NonWorkingDays = 0
    Schedule = {}
    for obj in schedule:
      val = self.calculateHours(obj)
      if val == 0.0: NonWorkingDays += 1
      else:
        TotalHours += val[1]
        Schedule.update(val[0])
    TotalWorkingDays = 7 - NonWorkingDays
    BreakHours = TotalWorkingDays * 0.5
    TotalHours -= BreakHours
    return (Schedule,{'ID' : data['EMP_ID'],
                      'NAME' : data['NAME'],
                      'HOURS' : TotalHours})
    
  def swap(self, data, target, id) -> dict:
    tTime = data[target]['HOURS']
    swapsuggestions = []
    for emd_id in self.employees:
      if emd_id != id:
        df1, df2 = self.fetch(emd_id)
        df1 = pd.DataFrame(df1)
        data = dict(df1.iloc[0])
        if(not data.__contains__(target)):
          for day, time in data.items():
            if time == tTime:
              data = {'NAME' : (str(df2['NAME'])), 'DAY' : day, 'EUID': str(df2['ID'])}
              swapsuggestions.append(data)
    return swapsuggestions
    

class App:

  def login(self, request):
    if request.method == "POST":
        uid = request.POST.get('u-id')
        key = request.POST.get('password')
        # confirm from db
        if(True):
          uid = SED().encrypt(uid)
          if('NULL' in uid.split('x')):
              return redirect('/user-not-found-error?err=404')
          return redirect(f'/home?id={uid}')
    return render(request, 'login.html')
  
  def _404unf(self, request):
    return render(request, '404.html')
  
  def URL(self, url):
    import re
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
    new_url = re.sub(pattern, replacement, url)

    return new_url
  
  def home(self, request):
    schedule = pd.read_csv(self.URL('https://docs.google.com/spreadsheets/d/12M2qwsqWd_APMf-GG-mZKZHWNdKGQMkABz9ugp92_kQ/edit#gid=1436417124'))
    esm = EmployeeScheduleManager(schedule)
    emps = esm.getEmployees()
    K = request.GET.get('id')  
    ID = SED().decrypt(K)
    if ID == 'NULL' or ID not in emps:
      return redirect('/user-not-found-error?err=404')
    df1, df2 = esm.fetch(ID)
    v = list(df1.values())
    V = []
    X = []
    for i in v:
      V.append(list(i.values())[0])
      X.append(list(i.values())[1])
       
    if request.method == "POST":
      target = request.POST.get('btn')
      suggestions = esm.swap(df1, target, ID)
      return self.swap(request, suggestions, ID, target)
      
      
    return render(request, 'home.html', {'payload': zip(list(df1.keys()), V, X), 'name': df2['NAME'], 'Hrs': df2['HOURS'] })
  
  def swap(self, request, data, id, T):
    names = []
    days = []
    euid = []
    encuid = []
    for d in data:
      for K, V in d.items():
        if K == 'NAME':
          names.append(V)
        if K == 'DAY':
          days.append(V)
        if K == 'EUID':
          euid.append(V)
          encuid.append(SED().encode(V))
    id_ = id
    T_ = T    
    status = False if len(names) == 0 else True
    return render(request, 'swap.html', {'data': zip(names, days, euid, encuid), 'sd' : SED().encode(id_), 'T': T_, 'status': status})
    
  def signup(self, request):
    if request.method == "POST":
        name = request.POST.get('username')
        email = request.POST.get('email')
        key = request.POST.get('password')
        ckey = request.POST.get('ckey')
        # save values to db
        if(key == ckey):
          return redirect('/log-in')
 
    return render(request, 'signup.html')
  
  def decode(self, state):
    settings = {
      "e" : "0", 
      "f" : "1", 
      "0" : "2", 
      "3" : "3", 
      "a" : "4", 
      "d" : "5", 
      "5" : "6", 
      "c" : "7", 
      "b" : "8", 
      "2" : "9", 
      "E" : ":", 
      "m" : "-", 
      "A" : ".", 
      "S" : " ", 
    }
    return "".join([settings.get(i) for i in state])
  
  def swapAccept(self, request):
    import datetime
    _selfUser = SED().decode(request.GET.get('_sid'))
    _target = request.GET.get('_T')
    reqUser = SED().decode(request.GET.get('rId'))
    _reqT = request.GET.get('_rsd')
    state = str(request.GET.get('rt_'))
    state = self.decode(state)
    _state = str(datetime.datetime.now())
    THRESHOLD = 5
    if request.method == "POST":
      if state.split()[0] == _state.split()[0]:
        timeStamp = state.split()[1].split('.')[0]
        _timeStamp = _state.split()[1].split('.')[0]
        if timeStamp.split(':')[0] == _timeStamp.split(':')[0]:
          if int(_timeStamp.split(':')[1]) < (int(timeStamp.split(':')[1]) + THRESHOLD):
            id = _selfUser
            password = request.POST.get('ckey')
            # confirm from database
            if(True):
              esm = EmployeeScheduleManager(pd.read_csv(self.URL('https://docs.google.com/spreadsheets/d/12M2qwsqWd_APMf-GG-mZKZHWNdKGQMkABz9ugp92_kQ/edit#gid=1436417124')))
              i = 0
              IDS = list(esm.data['EMP_ID'])
              seldUidx = -1
              reqUidx = -1
              for _id_ in range(len(IDS)):
                if id == IDS[_id_]:
                  seldUidx = _id_
                if reqUser == IDS[_id_]:
                  reqUidx = _id_
              if seldUidx != -1 and reqUidx != -1:
                try:
                  self_ = (esm.data.iloc[seldUidx])
                  req_ = (esm.data.iloc[reqUidx])
                  self_time = self_[_target]
                  req_time = req_[_reqT]
                  esm.data.iloc[seldUidx][_target] = 'X'
                  esm.data.iloc[seldUidx][_reqT] = req_time
                  esm.data.iloc[reqUidx][_reqT] = 'X'
                  esm.data.iloc[reqUidx][_target] = self_time
                  import os
                  PATH = "C://Users//"
                  PATH += os.listdir(PATH)[os.listdir(PATH).__len__()-1]+"//Desktop//ES.csv"
                  esm.data.to_csv(PATH)  
                  return self.reqAccepted(request)
                except Exception as e:
                  return redirect('/user-not-found-error?err=404')
              else:
                return redirect('/user-not-found-error?err=404')
          else:
            return redirect('/link-configuration-ended')
        else:
            return redirect('/link-configuration-ended')
    return render(request, 'accept.html')
  
  def linkUnavail(self, request):
    return render(request, 'Link.html')
  
  def reqAccepted(self, request):
    return render(request, 'reqAcc.html')