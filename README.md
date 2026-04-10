# Backend - Sistema de Emergencias Vehiculares

Guia rapida para levantar el backend en local (FastAPI).

## 1) Requisitos

- Windows con PowerShell
- Python 3.10 o superior
- PostgreSQL (si vas a usar base de datos local)

## 2) Clonar y entrar al proyecto

```powershell
git clone <URL_DEL_REPOSITORIO>
Set-Location "backend_emergencia_vehiculares"
```

## 3) Entorno virtual

Este proyecto ya trae una carpeta `env/`. Si existe en tu copia, activala:

```powershell
.\env\Scripts\Activate.ps1
```

Si no existe, crea una nueva:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

## 4) Instalar dependencias

```powershell
pip install -r requirements.txt
```

## 5) Configurar variables de entorno

Copia el archivo de ejemplo y ajusta tus valores:

```powershell
Copy-Item .env.exampe .env
```

Variables esperadas en `.env`:

- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Ejemplo rapido de conexion local con esas variables:

```dotenv
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_emergencias
```

## 6) Levantar el servidor

```powershell
uvicorn app.main:app --reload
```

La API quedara disponible en:

- `http://127.0.0.1:8000/`
- Docs Swagger: `http://127.0.0.1:8000/docs`

## 7) Verificacion rapida

Con el servidor corriendo, abre en navegador:

- `http://127.0.0.1:8000/`

Respuesta esperada:

```json
{
  "status": "Online",
  "message": "API de Emergencias Vehiculares lista"
}
```

## Estructura basica

```text
backend_emergencia_vehiculares/
  app/
    main.py
  requirements.txt
  .env.exampe
```

## Flujo recomendado para primera vez

1. Activar entorno virtual.
2. Instalar dependencias.
3. Crear `.env` desde `.env.exampe`.
4. Ajustar `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y `DB_NAME` en `.env`.
5. Ejecutar `uvicorn app.main:app --reload`.

## Notas

- Si PowerShell bloquea scripts, ejecuta una vez:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- Si cambias dependencias, actualiza `requirements.txt`.

