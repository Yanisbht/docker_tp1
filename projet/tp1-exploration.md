# TP1 : Exploration des API Docker et NetBox

## 1. Lancement des conteneurs

```bash
docker run -d --name web1 --label adminapi.managed=true nginx:alpine
docker run -d --name intrus nginx:alpine