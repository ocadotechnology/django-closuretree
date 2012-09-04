#!/bin/bash
cd testclosure
./manage.py jenkins closuretree tclosure
cd ..
rm -r reports
mv testclosure/reports .
