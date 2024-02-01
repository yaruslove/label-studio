
## Reference from 
 

[LS+SAM](https://github.com/HumanSignal/label-studio-ml-backend/tree/master/label_studio_ml/examples/segment_anything_model)

[Offical doc LS + SAM](https://labelstud.io/blog/get-started-using-segment-anything/)

## Pull docker label-studio
```
sudo docker pull heartexlabs/label-studio:latest
```

### Enabling Local Storage File Serving  
You can enable local storage file serving by setting the following variables.

```
LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=<path_to_image_data>
LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
```

### run image
I replaced default port to 4537
```
sudo docker run -it -p 4537:8080 \
    -v /home/yaroslav/ls_data:/label-studio/data \
    --env LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
    --env LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/label-studio/data \
    heartexlabs/label-studio:latest
```

### Setting Up the SAM Backend

Make a clone of this repository on your host system and move into the working directory.

```
git clone https://github.com/humansignal/label-studio-ml-backend
cd label-studio-ml-backend/label_studio_ml/examples/segment_anything_model
```

We suggest using Docker Compose to host and run the backend. For GPU support, please consult the Docker Compose GPU Access Guide to understand how to pass through GPU resources to services.  


Edit the `docker-compose.yml` file and fill in the values for the `LABEL_STUDIO_HOST` and `LABEL_STUDIO_ACCESS_TOKEN` for your particular installation. Be sure to append the port that Label Studio is running on in your LABEL_STUDIO_HOST variable, for example `http://192.168.1.36:8080` if Label Studio is running on port 8080 or i replaced to 4537.  
Run the command `docker compose up --build` to build the container and run it locally.
I replaced default port to 4537 in `docker-compose.yml`


example my config is: 
[docker-compose.yml](docker-compose.yml)


### Set up a Project in Label Studio for Segment Anything
Log into your Label Studio instance and perform the following steps.

Create a new project.
Under the Labeling Setup in the Create Project interface, or under the Labeling Interface menu item in the project settings, paste the sample template into the code dialog. Save the interface.
Under the Machine Learning menu item in the project settings, select Add Model.
Enter a title for the model, and the URL for the instance of the model you just created. If you're running Label Studio in Docker or on another host, you should use the direct IP address of where the model is hosted (localhost) will not work. Be sure to include the port number that the model is hosted on (the default is 9090). For example, if the model is hosted on 192.168.1.36, the URL for the model would be http://192.168.1.36:9090
Click Validate and Save.

```
<View>
  <Image name="image" value="$image" zoom="true"/>
  <Header value="Brush Labels"/>
  <BrushLabels name="tag" toName="image">
  	<Label value="Dog" background="#FF0000"/>
  	<Label value="Possum" background="#0d14d3"/>
  </BrushLabels>
  <Header value="Keypoint Labels"/>
  <KeyPointLabels name="tag2" toName="image" smart="true">
    <Label value="Dog" smart="true" background="#000000" showInline="true"/>
    <Label value="Possum" smart="true" background="#000000" showInline="true"/>
  </KeyPointLabels>
  <Header value="Rectangle Labels"/>
  <RectangleLabels name="tag3" toName="image" smart="true">
    <Label value="Dog" background="#000000" showInline="true"/>
    <Label value="Possum" background="#000000" showInline="true"/>
  </RectangleLabels>
</View>
```