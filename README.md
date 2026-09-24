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

## Publicación del asiento al confirmar pagos (Odoo 19)

Una cuenta de pagos pendientes no conciliable puede hacer que Odoo calcule el
pago como `paid` cuando su asiento todavía está en borrador. La confirmación
estándar puede omitir entonces ese pago y el asistente no concilia sus apuntes
con la factura, porque solo aplica apuntes publicados.

Después de la confirmación estándar, el módulo publica únicamente los asientos
que siguen en borrador de los pagos confirmados (`in_process` o `paid`). Conserva
las validaciones y permisos de Odoo. No fuerza el estado de la factura ni crea
un segundo pago. Las cuentas conciliables mantienen el flujo de conciliación
bancaria y los pagos parciales conservan su saldo pendiente.

El cambio actúa al confirmar pagos; no corrige registros anteriores de forma
masiva. Los pagos existentes con asiento en borrador deben revisarse y publicar
su asiento y aplicarlo a la factura correspondiente.

Antes de desplegar en producción, ejecutar en una base de pruebas:

```sh
odoo-bin -c /ruta/odoo.conf -d BASE_DE_PRUEBAS -u blautech --test-enable --test-tags /blautech:TestPaymentEntryPosting --stop-after-init
```

Las pruebas cubren facturas y pagos en distintas monedas, cuentas pendientes
conciliables y no conciliables, pagos parciales, confirmación repetida y el flujo
sin cuenta de pagos pendientes. Fuerzan el recálculo del estado antes de confirmar
para reproducir la secuencia que dejaba el asiento sin publicar.
