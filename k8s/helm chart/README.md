# argilla-helm-chart

 1. Init helm chart
 ```
 helm create argilla
 ```

 2. Deploy the helm chart
 ```
helm install argilla-chart argilla/ --values argilla/values.yaml --set enableOptionalResource=false
 ```