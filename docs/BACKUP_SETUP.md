# Configuración del respaldo diario (GitHub Actions)

## 1. Agregar Secrets en GitHub

Para que el workflow funcione, debes añadir las credenciales:

1. Ve a [github.com/Care-tech-innovations/mini_crm](https://github.com/Care-tech-innovations/mini_crm)
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**
4. **Mínimo obligatorio:** crea el secret **SUPABASE_KEY** (clave anon de Supabase, la misma que en Streamlit / `.env`).
5. **Opcional:** **SUPABASE_URL** = `https://mjylvwhyxnoqlieuhapv.supabase.co` — si no lo añades, el workflow usa la URL por defecto del proyecto.

### Organization secrets (Care-tech-innovations)

Si los secrets están en la **organización** y no en el repo:

1. **Organization** → **Settings** → **Secrets and variables** → **Actions**
2. Abre **SUPABASE_KEY** (y **SUPABASE_URL** si existe)
3. **Repository access** → asegúrate de que el repositorio **mini_crm** esté incluido.

Sin acceso al repo, el workflow recibe valores vacíos y falla.

## 2. Probar el workflow

1. **Actions** → **Backup clientes diario**
2. **Run workflow** → **Run workflow**
3. Espera que termine (verde ✓)
4. En la ejecución → **Artifacts** → descarga el backup

## 3. Fusionar a main (para que corra automático cada día)

1. Crear Pull Request: `feature/backup-diario` → `main`
2. Merge
3. El respaldo se ejecutará diariamente a las 6:00 AM UTC (~1:00 AM Ecuador)

## Horario

- **Automático:** Diario a las 6:00 AM UTC
- **Manual:** Actions → Backup clientes diario → Run workflow
