#!/usr/bin/env python3

# Find dates for exams at UniPD

"""
Copyright 2022 Davide Peressoni

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys, csv, requests, datetime, json
from queue import PriorityQueue

# CSV file with all the desired courses
# The first column must be the course code
COURSES_LIST = sys.argv[1] if len(sys.argv) == 2 else "courses.csv"

# Dates where to find exams
today = datetime.date.today()
BEGIN_DATE = today.strftime("%d-%m-%Y")
END_DATE = (today + datetime.timedelta(days = 2 * 30)).strftime("%d-%m-%Y")


class Exam:
  def __init__(self, code, *data):
    self.code = code.strip()
    self.data = [value.strip() for value in data]

  def __lt__(self, other):
    return self.code.__lt__(other.code)

  def __str__(self):
    return ', '.join([self.code] + self.data)

exams = []

with open(COURSES_LIST, newline='') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
  for row in spamreader:
    exams.append(Exam(*row))

exam_dates = PriorityQueue()

tot = len(exams)
for i, exam in enumerate(exams):
  data = json.loads(requests.post("https://agendastudentiunipd.easystaff.it/test_call.php", {
    "et_er" : "1",
    "esami_insegnamento" : exam.code,
    "datefrom" : BEGIN_DATE,
    "dateto" : END_DATE,
    }).text)

  print(f"{i+1}/{tot}\t{exam.code}", file=sys.stderr)

  for i in (ins := data["Insegnamenti"]):
    for app in ins[i]["Appelli"]:
      exam_dates.put((
        datetime.datetime.strptime(app["Data"], '%d-%m-%Y'),
        exam
      ))

last = [None, Exam("")]
while not exam_dates.empty():
  app = exam_dates.get()
  if last[0] != app[0] or last[1].code != app[1].code:
    print(app[0].strftime("%d/%m/%Y"), str(app[1]))
  last = app
