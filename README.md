## fpgaol-caas-backend

#### How to run this project

On host machine, pull the server and desired backends: 

`docker pull regymm/openxc7`

`docker pull regymm/vivado-lite`

`docker pull regymm/fpgaol-caas-backend`

Backend descriptions are at https://github.com/FPGAOL-CE/osstoolchain-docker-things .

Prepare working directories: 

```
sudo mkdir /chipdb && sudo chmod 777 /chipdb
sudo mkdir /jobs && sudo chmod 777 /jobs
```

Run the server in Docker: 

`docker run -it --rm -p 18888:18888 -v /var/run/docker.sock:/var/run/docker.sock -v /chipdb:/chipdb -v /jobs:/jobs regymm/fpgaol-caas-backend`

Server will be at localhost:18888. For frontend, please check https://github.com/FPGAOL-CE/fpgaol-caas-frontend . 



--- Deprecated ---

`pip install tornado aiofiles`

`uuidgen > token` For management panel access http://127.0.0.1:18888/jobs?token=uuid_in_token_file. 

Then check at http://127.0.0.1:18888. To serve frontend and backend together, you can overwrite the `page/` files using the built frontend(`dist/` from `fpgaol-caas-frontend`). 
