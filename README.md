Wordle Hint App
---------------

The corpus and word ranking functions are stored in `data_source.py`. 

To run the app, run `python main.py`.


## Docker commands

```shell
# To build image
docker image build -t danielbok/wordle-dash-app:0.0.1 .

# To test run container
docker container run --rm -p 8080:80 --name wordle danielbok/wordle-dash-app:0.0.1
```
