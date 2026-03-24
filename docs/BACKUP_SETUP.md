# Configuración del respaldo diario (GitHub Actions)

## 1. Agregar Secrets en GitHub

Para que el workflow funcione, debes añadir las credenciales:

1. Ve a [github.com/Care-tech-innovations/mini_crm](https://github.com/Care-tech-innovations/mini_crm)
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**
4. Crea dos secrets:
   - **SUPABASE_URL** = `https://mjylvwhyxnoqlieuhapv.supabase.co`
   - **SUPABASE_KEY** = tu clave anon de Supabase (la misma de tu `.env`)

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
