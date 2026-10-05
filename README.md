<img src="itsm/public/favicon.png" width="100" height="100" alt="Lambda" />

# Lambda

## Problem Statement
An IT services company keeps client onboarding documents, SLAs, and runbooks for hundreds of accounts, but support teams cannot quickly retrieve the correct, account-specific procedure during incidents. 

## Proposed Solution
An AI-powered Client Support Knowledge Assistant that:
Understands the context of an incident
Retrieves the most relevant client-specific information from multiple sources
Provides support teams with accurate procedures and guidance

## Architecture
We have two 'systems' working here:

### LambdaITSM
[LambdaITSM](https://lambda-itsm.netlify.app)


LamdaITSM is a sample client dashboard that connects with the core lambda bot for getting assistance during incidents. 
Technically, a React Dashboard with pre-built incidents and a chat sidebar that helps the support engineer to get the best assistance for an incident.

### Lambda Wiki
[Lambda Wiki](https://lambda-wiki.onrender.com)

Lambda Wiki is a sample wiki site that contains all the client-specific runbooks and SLAs. Technically, the core data lives inside supabase, the wiki is a flask. We are using flask templates to render the wiki site while the api routes fetch the mentioned data from supabase.

### Ingestion Service
There is an undeployed ingestion service which, in a real setting, will run periodically. It will source data from all the data sources, chunk it, embed it and push to supabase. 

## Data Sources
There are two data sources:
1. Wiki API - As mentioned, this is an interface to source data that lives inside supabase. This includes SLA contracts and runbooks.
2. Google Drive - Google Drive contains the client onboarding documents. 

For similarity search across vectors we are using pgvector inside supabase. So in case the bot needs to find relevant runbooks or COD docs, it embeds the incident context using Sentence Transformer and then queries supabase. While replying back to the user, it embeds a resource object that contains title and links to the resource.  

