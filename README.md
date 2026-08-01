# Books API — Azure APIM Lab

FastAPI Books API secured and managed through Azure API Management, with rate limiting, 
JWT-ready policies, conditional access rules, CI/CD via GitHub Actions, and full 
observability through Application Insights.

## Cleanup & Cost Optimization

### Cleanup Steps

The lab resource group (`AzureDevelopers-MoringaSchool`) is shared across multiple 
students' environments. To avoid impacting other students' work, individual resources 
were deleted rather than running a full resource group deletion.

If resources were exclusively owned, the full teardown command would be:

```bash
az group delete --name rg-books-api-lab --yes --no-wait
```

Since the group is shared, cleanup was instead performed resource-by-resource:

```bash
# Delete the APIM instance (longest-running deletion, ~30-45 min)
az apim delete --name apim-books-api-vt2026vm \
  --resource-group AzureDevelopers-MoringaSchool --yes

# Delete the App Service
az webapp delete --name app-books-api-vt2026vm \
  --resource-group AzureDevelopers-MoringaSchool

# Purge or delete the ACR repository
az acr repository delete --name acrbooksapivt2026vm \
  --repository fastapi-books-api --yes

# Delete Application Insights
az monitor app-insights component delete --app appi-books-api-labvm \
  --resource-group AzureDevelopers-MoringaSchool
```

### Estimated Costs

| Resource | SKU/Tier | Estimated Daily Cost | Notes |
|---|---|---|---|
| API Management | Standard/Developer | ~$0.50–$2.50 | Largest cost driver; consider Developer tier for labs |
| App Service | Basic (B1) | ~$0.15–$0.20 | Linux container plan |
| Container Registry | Basic | ~$0.16 | Storage + minimal build minutes |
| Application Insights | Pay-as-you-go | ~$0.05–$0.20 | Based on ingested log volume |
| **Total (approx.)** | | **~$1–$3/day** | Scales with usage and testing frequency |

### Cost-Saving Tips

- Use **Developer** or **Consumption** tier for APIM in lab/training environments — Standard tier is significantly more expensive and unnecessary for learning purposes.
- Use **Basic (B1)** or **Free (F1)** App Service plans for non-production workloads.
- **Delete or stop resources immediately** after completing lab work rather than leaving them running — APIM in particular accrues cost continuously regardless of traffic.
- Run **`az acr purge`** periodically to clean up untagged/old container images and avoid storage cost creep.
- Set up **budget alerts** in Cost Management to get notified before spend exceeds expected thresholds.
- **Tag resources** consistently (e.g., `environment:lab`, `owner:<name>`) to make cost attribution and cleanup easier, especially in shared resource groups.
- Delete **Application Insights / Log Analytics workspaces** promptly — they continue to incur ingestion costs even when idle.
