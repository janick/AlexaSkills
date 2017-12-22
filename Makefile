LAMBDA	= 
ZIP	= $(PWD)/package.zip

all install upload: compile
	rm -f $(ZIP)
	zip $(ZIP) lambda_function.py
	( cd venv/lib/python2.7/site-packages; zip -r $(ZIP) requests certifi chardet idna urllib3 )
	aws lambda update-function-code --function-name $(LAMBDA) --zip-file fileb://$(ZIP)

compile:
	python lambda_function.py
