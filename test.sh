#!/bin/bash
cd testclosure
./manage.py jenkins closuretree
cd ..
rm -r reports
mv testclosure/reports .
