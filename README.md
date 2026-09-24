# blautech

## Códigos de cuenta para auditoría externa (Odoo 19)

El grupo `blautech.auditoria_externa` usa el menú de
`views/menu_item_views.xml`. Odoo 19 muestra el código en `account.account.display_name`
solo a los miembros de `account.group_account_readonly`, por lo que un auditor
con permisos propios de lectura veía únicamente el nombre en los informes.

El módulo añade el código al nombre para el grupo de auditoría externa, sin
añadir grupos, permisos ni menús. Conserva el formato nativo de las cuentas,
las sugerencias, las descripciones y el código de la compañía activa.

Después de desplegar el código, reiniciar Odoo y actualizar el módulo `blautech`
desde Aplicaciones, o ejecutar con la configuración y base de datos del entorno:

```sh
odoo-bin -c /ruta/odoo.conf -d BASE_DE_DATOS -u blautech --stop-after-init
```

Para ejecutar las pruebas de regresión en una base de pruebas con las dependencias
del módulo (incluidos `account_accountant` y `account_gt`):

```sh
odoo-bin -c /ruta/odoo.conf -d BASE_DE_PRUEBAS -u blautech --test-enable --test-tags /blautech --stop-after-init
```

Comprobar también con un usuario de auditoría externa: abrir Balance general,
desplegar las cuentas y verificar `código + nombre`, así como las exportaciones
PDF/XLSX. El acceso debe conservarse dentro de los permisos ya asignados al usuario.
