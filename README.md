## fpgaol-caas-backend

#### How to run this project

`docker pull regymm/symbiflow`
Or build from scratch according to https://github.com/FPGAOL-CE/osstoolchain-docker-things . The image is around 20 GB. 

`pip install tornado aiofiles`

`uuidgen > token` For management panel access http://127.0.0.1:18888/jobs?token=uuid_in_token_file. 

`python server.py` For some reason, nohup or setsid launch have problems. Tmux is recommended for keeping server alive. 

Then check at http://127.0.0.1:18888. To serve frontend and backend together, you can overwrite the `page/` files using the built frontend(`dist/` from `fpgaol-caas-frontend`). 
