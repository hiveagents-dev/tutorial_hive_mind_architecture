# 🏗️ Diagramas de Arquitectura - Plataforma de Aprendizaje Online

## 📋 Vista 1: Vista Lógica (Logical View)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISTA LÓGICA                                 │
│              Plataforma de Aprendizaje Online                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │   Application    │    │      Data       │
│     Layer       │    │     Layer        │    │     Layer       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Web Frontend  │    │ • Course Mgmt   │    │ • User Data      │
│ • Mobile App    │◄──►│ • Code Exec      │◄──►│ • Course Data   │
│ • Admin Panel   │    │ • Auth Service   │    │ • Progress Data │
│ • IDE Browser   │    │ • Payment Mgmt   │    │ • Analytics     │
└─────────────────┘    │ • Gamification   │    └─────────────────┘
                       │ • Notification   │
                       └─────────────────┘
```

**Componentes Principales:**
- **Frontend:** React/Next.js con IDE integrado
- **Backend:** Node.js/Express con microservicios
- **Code Execution:** Sandbox seguro con Docker
- **Database:** PostgreSQL + Redis Cache
- **File Storage:** AWS S3 para contenido multimedia

---

## ⚙️ Vista 2: Vista de Procesos (Process View)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISTA DE PROCESOS                           │
│              Flujos de Ejecución Principales                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │    │   Auth      │    │   Course    │    │   Code      │
│   Login     │───►│  Service    │───►│  Service    │───►│ Execution  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Session   │    │   JWT       │    │   Content   │    │   Sandbox   │
│  Management │    │  Token      │    │  Delivery   │    │  Container  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Progress  │    │   Payment   │    │   Analytics │    │   Grading   │
│  Tracking    │    │  Processing │    │   Service   │    │   Engine    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**Flujos Principales:**
1. **Autenticación y Autorización**
2. **Consumo de Contenido Educativo**
3. **Ejecución de Código en Sandbox**
4. **Evaluación Automática**
5. **Seguimiento de Progreso**
6. **Gamificación y Notificaciones**

---

## 🖥️ Vista 3: Vista Física (Physical View)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISTA FÍSICA                                │
│              Infraestructura y Deployment                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        AWS CLOUD                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Region    │  │   Region    │  │   Region    │            │
│  │  us-east-1  │  │  us-west-2  │  │  sa-east-1  │            │
│  │  (Primary)  │  │  (Backup)   │  │  (LATAM)    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   ECS       │  │   RDS       │  │   S3        │            │
│  │  Fargate    │  │ PostgreSQL  │  │  Storage    │            │
│  │  Containers │  │  Multi-AZ   │  │  Content    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   ALB       │  │   CloudFront│  │   ElastiCache│           │
│  │ Load Balancer│  │    CDN     │  │    Redis    │            │
│  │             │  │             │  │   Cache      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

**Infraestructura:**
- **Containerización:** Docker + ECS Fargate
- **Base de Datos:** PostgreSQL Multi-AZ
- **Cache:** Redis ElastiCache
- **Storage:** S3 para archivos multimedia
- **CDN:** CloudFront para contenido estático
- **Load Balancer:** Application Load Balancer
- **Monitoreo:** CloudWatch + X-Ray

---

## 💻 Vista 4: Vista de Desarrollo (Development View)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISTA DE DESARROLLO                         │
│              Estructura de Módulos y Paquetes                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Next.js)                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Pages     │  │ Components  │  │   Services  │            │
│  │ • /courses  │  │ • IDE       │  │ • API       │            │
│  │ • /profile  │  │ • Video     │  │ • Auth      │            │
│  │ • /dashboard│  │ • Progress  │  │ • Storage   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Utils     │  │   Hooks     │  │   Types     │            │
│  │ • Helpers   │  │ • useAuth   │  │ • Interfaces│            │
│  │ • Constants │  │ • useCourse │  │ • Enums     │            │
│  │ • Validators│  │ • useCode   │  │ • Types     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Node.js/Express)                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Routes    │  │  Services  │  │   Models    │            │
│  │ • /auth     │  │ • Auth     │  │ • User      │            │
│  │ • /courses  │  │ • Course   │  │ • Course    │            │
│  │ • /code     │  │ • Code     │  │ • Progress  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Middleware  │  │   Utils     │  │   Config    │            │
│  │ • Auth      │  │ • Logger    │  │ • Database  │            │
│  │ • Validation│  │ • Crypto    │  │ • Redis     │            │
│  │ • Error     │  │ • Helpers   │  │ • AWS       │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CODE EXECUTION SERVICE                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Docker    │  │   Grading   │  │   Security  │            │
│  │ Containers  │  │   Engine    │  │   Sandbox   │            │
│  │ • Node.js   │  │ • Test      │  │ • Isolation  │            │
│  │ • Python    │  │ • Results   │  │ • Limits    │            │
│  │ • Java      │  │ • Feedback  │  │ • Monitoring│            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Vista 5: Vista de Casos de Uso (Use Case View)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISTA DE CASOS DE USO                       │
│              Interacciones Usuario-Sistema                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        ACTORES                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Estudiante  │  │ Instructor  │  │   Admin     │            │
│  │             │  │             │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### 📚 Gestión de Cursos
- **Estudiante** ──► Ver cursos disponibles
- **Estudiante** ──► Inscribirse en curso
- **Estudiante** ──► Acceder a contenido
- **Instructor** ──► Crear/editar cursos
- **Instructor** ──► Subir contenido multimedia

### 💻 Ejecución de Código
- **Estudiante** ──► Abrir IDE en navegador
- **Estudiante** ──► Escribir código
- **Estudiante** ──► Ejecutar código en sandbox
- **Sistema** ────► Evaluar código automáticamente
- **Sistema** ────► Proporcionar feedback

### 🎮 Gamificación
- **Estudiante** ──► Completar ejercicios
- **Sistema** ────► Otorgar puntos y badges
- **Estudiante** ──► Ver progreso y logros
- **Estudiante** ──► Competir en leaderboards

### 💳 Gestión de Suscripciones
- **Estudiante** ──► Suscribirse mensualmente
- **Estudiante** ──► Gestionar método de pago
- **Sistema** ────► Procesar pagos
- **Sistema** ────► Renovar suscripción automáticamente

### 📊 Administración
- **Admin** ──────► Gestionar usuarios
- **Admin** ──────► Ver analytics y métricas
- **Admin** ──────► Configurar sistema
- **Admin** ──────► Monitorear rendimiento

---

## 🔒 Vista 6: Vista de Seguridad (Security View)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISTA DE SEGURIDAD                          │
│              Arquitectura de Seguridad                         │
└─────────────────────────────────────────────────────────────────┘
```

### 🌐 Capa de Red
- **HTTPS/TLS 1.3** obligatorio
- **WAF** (Web Application Firewall)
- **DDoS Protection**
- **Rate Limiting**

### 🔐 Capa de Autenticación
- **JWT Tokens** con expiración corta
- **Refresh Tokens** seguros
- **Multi-Factor Authentication** (MFA)
- **OAuth 2.0** para integraciones

### 🛡️ Capa de Aplicación
- **Input Validation** y Sanitization
- **SQL Injection Prevention**
- **XSS Protection**
- **CSRF Tokens**
- **Role-Based Access Control** (RBAC)

### 🏗️ Capa de Infraestructura
- **Container Security** (Docker)
- **Secrets Management** (AWS Secrets Manager)
- **Network Segmentation**
- **Encryption at Rest** (AES-256)
- **Encryption in Transit**

### 🔍 Capa de Monitoreo
- **Security Logging**
- **Intrusion Detection**
- **Anomaly Detection**
- **Security Incident Response**
- **Regular Security Audits**

### 🐳 Seguridad del Sandbox
- **Aislamiento completo** del código del usuario
- **Límites de recursos** (CPU, memoria, tiempo)
- **Red aislada** sin acceso a internet
- **Filesystem de solo lectura**
- **Proceso único** por container
- **Máximo 30 segundos** de ejecución
- **Timeout automático**
- **Cleanup inmediato** post-ejecución

---

## 📋 Resumen de Vistas Creadas

### ✅ 4 Vistas Estándar + 2 Adicionales:

1. **📋 Vista Lógica (Logical View)**
   - Componentes principales y sus responsabilidades
   - Separación en capas (Presentation, Application, Data)
   - Tecnologías utilizadas

2. **⚙️ Vista de Procesos (Process View)**
   - Flujos de ejecución principales
   - Interacciones entre servicios
   - Secuencia de operaciones

3. **🖥️ Vista Física (Physical View)**
   - Infraestructura de deployment
   - Servicios de AWS utilizados
   - Configuración de alta disponibilidad

4. **💻 Vista de Desarrollo (Development View)**
   - Estructura de módulos y paquetes
   - Organización del código
   - Separación de responsabilidades

5. **🎯 Vista de Casos de Uso (Use Case View)** ⭐ *Adicional*
   - Actores del sistema
   - Casos de uso principales
   - Interacciones usuario-sistema

6. **🔒 Vista de Seguridad (Security View)** ⭐ *Adicional*
   - Capas de seguridad implementadas
   - Medidas de protección
   - Seguridad específica del sandbox

---

## 🎯 Conclusión

**Todas las vistas están alineadas con los requisitos técnicos generados por HiveMind para la plataforma de aprendizaje online.**

Los diagramas muestran una arquitectura robusta, escalable y segura que cumple con:
- ✅ **Requisitos funcionales** (IDE integrado, evaluación automática)
- ✅ **Requisitos no funcionales** (escalabilidad, seguridad, rendimiento)
- ✅ **Restricciones de LATAM** (conexiones lentas, presupuesto limitado)
- ✅ **Objetivos de negocio** (5,000 estudiantes, $200K ARR)

La arquitectura propuesta es **técnicamente viable** y **comercialmente sostenible** para el mercado objetivo.
