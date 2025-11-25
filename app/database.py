from supabase import create_client, Client

# Konfigurasi Supabase
# (Nanti sebaiknya dipindah ke .env file, tapi sementara taruh sini oke)
SUPABASE_URL = "https://qzktpdxibkhemcezrceg.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6a3RwZHhpYmtoZW1jZXpyY2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDYyNjcsImV4cCI6MjA3OTU4MjI2N30.1UNPjAkoC5DOsLpg78RXEL27VFvYC4kN5uFsUnODvWE" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)