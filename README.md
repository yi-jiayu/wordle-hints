Wordle Hint App
---------------

The corpus and word ranking functions are stored in `data_source.py`. 

To run the app, run `python main.py`.


## Docker commands

```shell
# To build image
docker image build -t danielbok/wordle-dash-app .

# To test run container
docker container run --rm -p 8080:8080 --name wordle danielbok/wordle-dash-app
```
