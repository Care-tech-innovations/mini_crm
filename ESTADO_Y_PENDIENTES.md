# Estado actual y pasos pendientes

## ✅ Ya completado

| Elemento | Estado |
|----------|--------|
| Código Supabase | ✓ En `main` |
| clients.json | ✓ 17 clientes |
| Tabla en Supabase | ✓ `Ramayana's Clients` |
| Migración de datos | ✓ 17 clientes en Supabase |

---

## Si la app sale vacía: verificar

### 1. Indicador en la sidebar

Al abrir la app, mira la **parte inferior del menú lateral**:

- **✓ Datos: Supabase** → Supabase conectado. Si sigue vacía, revisa RLS en Supabase.
- **⚠ Datos: archivo local** → Secrets no configurados. Sigue el paso 2.

### 2. Formato exacto de Secrets (Streamlit Cloud)

1. [share.streamlit.io](https://share.streamlit.io) → tu app → **Settings** → **Secrets**
2. Pegar **exactamente** (mismo formato, sin comillas extra):

```toml
SUPABASE_URL = "https://mjylvwhyxnoqlieuhapv.supabase.co"
SUPABASE_KEY = "tu_clave_anon_aqui"
```

- Los nombres deben ser **SUPABASE_URL** y **SUPABASE_KEY** (mayúsculas).
- Usa el signo `=` con espacios.
- La clave es la **anon (public)** de Supabase, no la service_role.

### 3. Repositorio de despliegue

Confirma que la app está conectada a **Care-tech-innovations/mini_crm** (o que tu fork está sincronizado con ese repo).

### 4. Reboot

Después de cambiar Secrets: **Reboot** y esperar 2–3 minutos.
