{{/*
Expand the name of the chart.
*/}}
{{- define "speckit-mcp-server.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "speckit-mcp-server.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "speckit-mcp-server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "speckit-mcp-server.labels" -}}
helm.sh/chart: {{ include "speckit-mcp-server.chart" . }}
{{ include "speckit-mcp-server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "speckit-mcp-server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "speckit-mcp-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Validate deployment mode
Fails fast if mode is not "image" or "npm"
*/}}
{{- define "speckit-mcp-server.validateMode" -}}
{{- if and (ne .Values.mode "image") (ne .Values.mode "npm") }}
{{- fail (printf "Invalid deployment mode '%s'. Must be 'image' or 'npm'" .Values.mode) }}
{{- end }}
{{- end }}

{{/*
Validate mutual exclusivity of ingress and httpRoute
Fails fast if both are enabled
*/}}
{{- define "speckit-mcp-server.validateRouting" -}}
{{- if and .Values.ingress.enabled .Values.httpRoute.enabled }}
{{- fail "Cannot enable both ingress and httpRoute. They are mutually exclusive. Set only one to enabled=true" }}
{{- end }}
{{- end }}
