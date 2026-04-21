{{- define "blurmoji.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "blurmoji.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

