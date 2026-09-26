Para levantar el compose (en windows cmd):

1) clonar el repositorio: >git clone -b lab07 https://github.com/ivanabregooo-web/ciencia-de-datos-pdcb.git .

2) entrar a la carpeta correcta: >cd entrega-Lab07

3) copiar las credenciales: >copy .env.example .env

4) levantarlo:
	- sin adminer: >docker compose up --build -d
	- con adminer: >docker compose --profile dev up --build -d

5) tumbarlo:
	- sin adminer: >docker compose down 
	- con adminer: >docker compose --profile dev down