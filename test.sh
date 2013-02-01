#!/bin/bash
cd test_project
./manage.py jenkins closuretree
cd ..
rm -r reports
mv test_project/reports .
