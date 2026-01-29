import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, CircularProgress, Grid, List, ListItem, ListItemText } from '@mui/material';

type ClusteringResults = {
  metrics?: any;
  profiles?: Record<string, any[]>;
};

const detectClusterKey = (row: any) => {
  const keys = Object.keys(row || {});
  return keys.find(k => /cluster|label|cluster_id/i.test(k)) || null;
};

const simpleCounts = (rows: any[]) => {
  const counts: Record<string, number> = {};
  if (!rows || rows.length === 0) return counts;
  const key = detectClusterKey(rows[0]);
  if (!key) {
    counts['all'] = rows.length;
    return counts;
  }
  rows.forEach(r => {
    const v = String(r[key]);
    counts[v] = (counts[v] || 0) + 1;
  });
  return counts;
};

const BarChart: React.FC<{counts: Record<string, number>}> = ({ counts }) => {
  const entries = Object.entries(counts);
  const max = Math.max(...entries.map(([,v]) => v), 1);
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {entries.map(([k,v]) => (
        <Box key={k} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 80, fontSize: 13 }}>{k}</Box>
          <Box sx={{ flex: 1, background: '#eee', height: 16, borderRadius: 4 }}>
            <Box sx={{ width: `${(v/max)*100}%`, height: '100%', background: '#2e7d32', borderRadius: 4 }} />
          </Box>
          <Box sx={{ width: 40, textAlign: 'right', fontSize: 13 }}>{v}</Box>
        </Box>
      ))}
    </Box>
  );
};

const ClustersView: React.FC = () => {
  const [results, setResults] = useState<ClusteringResults | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const stored = localStorage.getItem('clustering_results');
        if (stored) {
          setResults(JSON.parse(stored));
          setLoading(false);
          return;
        }
        const resp = await fetch('http://localhost:8000/results/clustering');
        if (!resp.ok) throw new Error('Failed to fetch clustering results');
        const data = await resp.json();
        setResults(data.data || null);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}><CircularProgress /></Box>;
  if (!results) return <Box sx={{ padding: 4 }}><Typography>No clustering results available.</Typography></Box>;

  const profiles = results.profiles || {};

  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" sx={{ marginBottom: 2 }}>Cluster Results</Typography>
      <Grid container spacing={2}>
        {Object.keys(profiles).map((profileName) => {
          const rows = profiles[profileName] || [];
          const counts = simpleCounts(rows);
          return (
            <Grid item xs={12} md={6} key={profileName}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>{profileName.replace(/_/g, ' ')}</Typography>
                  <Box sx={{ marginY: 2 }}>
                    <BarChart counts={counts} />
                  </Box>
                  <Typography variant="subtitle2">Cluster descriptions / samples</Typography>
                  <List dense>
                    {Object.entries(counts).map(([cluster, cnt]) => (
                      <ListItem key={cluster} sx={{ alignItems: 'flex-start' }}>
                        <ListItemText
                          primary={`Cluster ${cluster} — ${cnt} customers`}
                          secondary={
                            rows.filter(r => String(r[detectClusterKey(rows[0])]) === cluster).slice(0,3).map(r => (
                              <div key={JSON.stringify(r)} style={{ fontSize: 12, color: '#444' }}>{Object.entries(r).slice(0,4).map(([k,v])=>`${k}: ${v}`).join(' · ')}</div>
                            ))
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};

export default ClustersView;
