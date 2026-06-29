{{- define "blurmoji.name" -}}
    {{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this.
If release name contains chart name it will be used as a full name.
*/}}
{{- define "blurmoji.fullname" -}}
    {{- if .Values.fullnameOverride -}}
        {{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
    {{- else -}}
        {{- $name := default .Chart.Name .Values.nameOverride -}}
    {{- if contains $name .Release.Name -}}
        {{- .Release.Name | trunc 63 | trimSuffix "-" -}}
    {{- else -}}
        {{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
    {{- end -}}
    {{- end -}}
{{- end -}}

{{- define "blurmoji.appImage" -}}
{{- printf "%s:%s" .Values.images.app.repository .Values.images.app.tag -}}
{{- end -}}

{{- define "blurmoji.redisImage" -}}
{{- printf "%s:%s" .Values.images.redis.repository .Values.images.redis.tag -}}
{{- end -}}

{{- define "blurmoji.curlImage" -}}
{{- printf "%s:%s" .Values.images.curl.repository .Values.images.curl.tag -}}
{{- end -}}

