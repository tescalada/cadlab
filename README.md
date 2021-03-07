# cadlab
CADLab - cadquery customizer


To use this repo, you just need to add a dockerfile to your folder containing your assemblies.

Dockerfile
```
FROM docker.pkg.github.com/tescalada/cadlab/cadlab:latest

# add your assemblies into the assemblies folder
ADD . /opt/webapp/assemblies/
```

Then run the dockerfile and the app should pick up your models. You can push your app to heroku with the commands
```
# create your app
heroku create YOUR_APP_NAME

# login to the registry
heroku container:login

# build and push your app to the registry
heroku container:push web

# deploy your containter to the web
heroku container:release web

# open your app
heroku open
```

checkout the example assemblies to see the expected format for the Form class and make function. The make function needs to accept the Form params as inputs and must return a dict in the form
```
    {
        'version': version,
        'parameters': {**form_params},
        'parts': {
            'part_name': cadquery_model,
        },
    }
```
