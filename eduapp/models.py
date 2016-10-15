from __future__ import unicode_literals

from django.db import models
from urllib2 import urlopen

import json

sdf13_url = "http://ec2-54-167-155-28.compute-1.amazonaws.com:9200/_all/sdf13/_search?size=1000&q=*:*"
enroll_url = "http://ec2-54-167-155-28.compute-1.amazonaws.com:9200/_all/enroll-fix/_search?size=1000&q=*:*"
sat_url = "http://ec2-54-167-155-28.compute-1.amazonaws.com:9200/_all/sat/_search?size=1000&q=*:*"

name_maps = {
    "ARLINGTON MEMORIAL HIGH SCHOOL": "ARLINGTON SCHOOL DISTRICT",
    "CABOT SCHOOL": "CABOT SCHOOL DISTRICT",
    "CHELSEA ELEM HIGH SCHOOL": "CHELSEA SCHOOL DISTRICT",
    "COLCHESTER HIGH SCHOOL": "COLCHESTER SCHOOL DISTRICT",
    "MONTPELIER HIGH SCHOOL": "MONTPELIER SCHOOL DISTRICT",
    "PROCTOR JR/SR HIGH SCHOOL": "PROCTOR SCHOOL DISTRICT",
    "RICHFORD JR/SR HIGH SCHOOL": "RICHFORD SCHOOL DISTRICT",
    "BURLINGTON SENIOR HIGH SCHOOL": "BURLINGTON SCHOOL DISTRICT",
    "ENOSBURG FALLS MIDDLE-HIGH SCHOOL": "ENOSBURGH TOWN SCHOOL DISTRICT",
    "MIDDLEBURY UNION HIGH SCHOOL": "MIDDLEBURY UHSD #3",
    "SO BURLINGTON HIGH SCHOOL": "SOUTH BURLINGTON SCHOOL DISTRICT",
    "POULTNEY HIGH SCHOOL": "POULTNEY SCHOOL DISTRICT",
    "WINDSOR SCHOOL": "WINDSOR SCHOOL DISTRICT",
    "WOODSTOCK SR UHSD #4": "WOODSTOCK UHSD #4",
    "DANVILLE SCHOOL": "DANVILLE SCHOOL DISTRICT",
    "ROCHESTER SCHOOL": "ROCHESTER SCHOOL DISTRICT",
    "RUTLAND HIGH SCHOOL": "RUTLAND CITY SCHOOL DISTRICT",
    "BELLOWS FREE ACADEMY (ST ALBANS)": "BELLOWS FREE ACADEMY UHSD #48",
    "BLACK RIVER US #39": "BLACK RIVER USD #39",
    "BLUE MOUNTAIN US #21": "BLUE MOUNTAIN USD #21",
    "CRAFTSBURY SCHOOLS": "CRAFTSBURY SCHOOL DISTRICT",
    "ESSEX HIGH SCHOOL": "ESSEX TOWN SCHOOL DISTRICT",
    "LYNDON INSTITUTE": "LYNDON SCHOOL DISTRICT",
    "NORTHFIELD MIDDLE/HIGH SCHOOL": "NORTHFIELD SCHOOL DISTRICT",
    "ST JOHNSBURY ACADEMY": "SAINT JOHNSBURY SCHOOL DISTRICT",
    "WINOOSKI HIGH SCHOOL": "WINOOSKI SCHOOL DISTRICT",
    "CONCORD GRADED/MIDDLE SCHOOL": "CONCORD SCHOOL DISTRICT",
    "HARTFORD HIGH SCHOOL": "HARTFORD SCHOOL DISTRICT",
    "MILL RIVER US #40": "MILL RIVER USD #40",
    "MILTON HIGH SCHOOL": "MILTON INCORPORATED SCHOOL DISTRICT",
    "MT ANTHONY SR UHSD #14": "MOUNT ANTHONY UHSD #14",
    "NORTH COUNTRY UHSD #22A": "NORTH COUNTRY SENIOR UHSD #22",
    "SPRINGFIELD HIGH SCHOOL": "SPRINGFIELD SCHOOL DISTRICT",
    "WEST RUTLAND SCHOOL": "WEST RUTLAND SCHOOL DISTRICT",
    "WILLIAMSTOWN MIDDLE/HIGH SCHOOL": "WILLIAMSTOWN SCHOOL DISTRICT",
    "CANAAN SCHOOLS": "CANAAN SCHOOL DISTRICT",
    "MT ABRAHAM UHSD #28": "MOUNT ABRAHAM UHSD #28",
    "MT MANSFIELD USD #401B": "MOUNT MANSFIELD USD #17",
    "SO ROYALTON ELEM/HIGH SCHOOL": "ROYALTON SCHOOL DISTRICT",
    "STOWE MIDDLE/HIGH SCHOOL": "STOWE SCHOOL DISTRICT",
    "THETFORD ACADEMY": "THETFORD SCHOOL DISTRICT",
    "TWINFIELD US #33": "TWINFIELD USD #33"

}

skip_set = [
    'School Name',
    'U32 UHSD #32',
    "PEOPLES ACADEMY",
    "TWIN VALLEY HIGH SCHOOL",
    "BURR AND BURTON ACADEMY",
    "WHITCOMB JR/SR HIGH SCHOOL",
    "BELLOWS FREE ACADEMY HS (FAIRFAX)",
    "BLACK RIVER USD #39",
    "CRAFTSBURY SCHOOL DISTRICT",
    "PROCTOR SCHOOL DISTRICT",
    "RICHFORD SCHOOL DISTRICT",
    "CHELSEA SCHOOL DISTRICT"
]

class SchoolDistrict:
    def totalRev(self):
        return self.stateRev + self.federalRev + self.localRev

    def __init__(self, leaid, name, localRev, stateRev, federalRev, pop, collegeEnrollRate, satMean):
        self.leaid = leaid

        self.name = name

        self.localRev = localRev
        self.stateRev = stateRev
        self.federalRev = federalRev

        self.pop = pop

        self.collegeEnrollRate = collegeEnrollRate

        self.satMean = satMean

    def getPerformanceMetric(self):
        satWeight = 0.5
        collegeEnrollRateWeight = 0.5

        if self.satMean == 0:
            satWeight = 0
            collegeEnrollRateWeight = 1

        return 100.0 * (self.satMean / 2400.0 * satWeight + self.collegeEnrollRate * collegeEnrollRateWeight)


    @staticmethod
    def getAll():
        sdf13_raw = [h['_source'] for h in json.loads(urlopen(sdf13_url).read())['hits']['hits']]

        enroll_raw = [h['_source'] for h in json.loads(urlopen(enroll_url).read())['hits']['hits']]

        sat_raw = [h['_source'] for h in json.loads(urlopen(sat_url).read())['hits']['hits']]

        district_map = {}

        for row in sdf13_raw:
            district_map[row['NAME']] = row

        for row in sat_raw:
            testTakers = row['Test Takers']
            satMean = row['Critical Reading Mean'] + row['Math Mean'] + row['Writing Mean']
            # since will rewrote thius data set we can be sure this aligns
            district_map[row['District']].update('satMean'=satMean, 'testTakers'=testTakers)

        result = []

        for row in enroll_raw:
            name = name_maps[row['School Name']] if row['School Name'] in name_maps else row['School Name']
            # <3 Will
            if name in skip_set:
                continue

            district = district_map[name]

            leaid = int(district['LEAID'])

            name = district['NAME']

            localRev = int(district['TLOCREV'])
            stateRev = int(district['TSTREV'])
            fedRev = int(district['TFEDREV'])

            pop = int(district['MEMBERSCH'])

            collegeEnrollRate = row['Postseconary Enrollment Rate'].strip("%")
            collegeEnrollRate = 0 if collegeEnrollRate == "++" else collegeEnrollRate
            collegeEnrollRate = float(collegeEnrollRate) / 100

            testTakers = int(district['testTakers'])
            satMean = int(district['satMean'])

            result.append(SchoolDistrict(leaid, name, localRev, stateRev, fedRev, pop, collegeEnrollRate, satMean, testTakers))


        return result
