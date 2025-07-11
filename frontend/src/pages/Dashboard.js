import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
} from '@mui/material';
import {
  WhatsApp,
  Message,
  People,
  TrendingUp,
  Schedule,
  CheckCircle,
  Error,
  Phone,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { useQuery } from 'react-query';
import axios from 'axios';
import { format } from 'date-fns';

const COLORS = ['#25D366', '#128C7E', '#075E54', '#34B7F1', '#FFC658', '#FF7C7C'];

const Dashboard = () => {
  const [whatsappStatus, setWhatsappStatus] = useState(null);

  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading } = useQuery(
    'dashboardStats',
    async () => {
      const response = await axios.get('/api/dashboard/stats');
      return response.data;
    },
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  // Fetch recent messages
  const { data: recentMessages, isLoading: messagesLoading } = useQuery(
    'recentMessages',
    async () => {
      const response = await axios.get('/api/messages?limit=10');
      return response.data;
    },
    { refetchInterval: 10000 } // Refresh every 10 seconds
  );

  // Fetch WhatsApp status
  const { data: statusData } = useQuery(
    'whatsappStatus',
    async () => {
      const response = await axios.get('/api/whatsapp/status');
      return response.data;
    },
    { refetchInterval: 5000 } // Refresh every 5 seconds
  );

  useEffect(() => {
    if (statusData) {
      setWhatsappStatus(statusData);
    }
  }, [statusData]);

  // Prepare data for charts
  const categoryData = stats?.category_stats
    ? Object.entries(stats.category_stats).map(([category, count]) => ({
        name: category.charAt(0).toUpperCase() + category.slice(1),
        value: count,
      }))
    : [];

  const messageFlowData = [
    { name: 'Incoming', messages: stats?.total_incoming || 0 },
    { name: 'Outgoing', messages: stats?.total_outgoing || 0 },
  ];

  const StatCard = ({ title, value, icon, color, subtitle, loading }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar sx={{ bgcolor: color, mr: 2 }}>
            {icon}
          </Avatar>
          <Box>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            {loading ? (
              <LinearProgress sx={{ width: 100 }} />
            ) : (
              <Typography variant="h4" fontWeight="bold">
                {value}
              </Typography>
            )}
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const WhatsAppStatusCard = () => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <WhatsApp sx={{ mr: 2, color: '#25D366' }} />
          <Typography variant="h6">WhatsApp Status</Typography>
        </Box>
        
        {whatsappStatus ? (
          <Box>
            <Chip
              label={whatsappStatus.connected ? 'Connected' : 'Disconnected'}
              color={whatsappStatus.connected ? 'success' : 'error'}
              icon={whatsappStatus.connected ? <CheckCircle /> : <Error />}
              sx={{ mb: 2 }}
            />
            
            {whatsappStatus.connected && (
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Phone: {whatsappStatus.phone_number || 'Not available'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Status: {whatsappStatus.status || 'Unknown'}
                </Typography>
                {whatsappStatus.last_seen && (
                  <Typography variant="body2" color="text.secondary">
                    Last seen: {format(new Date(whatsappStatus.last_seen), 'PPpp')}
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        ) : (
          <Alert severity="warning">
            Unable to fetch WhatsApp status
          </Alert>
        )}
      </CardContent>
    </Card>
  );

  const RecentMessagesCard = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Messages
        </Typography>
        
        {messagesLoading ? (
          <LinearProgress />
        ) : recentMessages && recentMessages.length > 0 ? (
          <List dense>
            {recentMessages.slice(0, 5).map((message) => (
              <ListItem key={message.id} divider>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: message.is_incoming ? '#25D366' : '#128C7E' }}>
                    {message.is_incoming ? (
                      <Message sx={{ transform: 'scaleX(-1)' }} />
                    ) : (
                      <Message />
                    )}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2" fontWeight="bold">
                        {message.contact_name || message.phone_number}
                      </Typography>
                      <Chip
                        label={message.classification?.category || 'Unclassified'}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                        {message.message_text}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(message.timestamp), 'MMM dd, HH:mm')}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No recent messages
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Welcome to your WhatsApp MCP Dashboard. Monitor your messaging activities and AI-powered interactions.
      </Typography>

      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Messages"
            value={stats?.total_messages || 0}
            icon={<Message />}
            color="#25D366"
            subtitle="All time"
            loading={statsLoading}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Contacts"
            value={stats?.total_contacts || 0}
            icon={<People />}
            color="#128C7E"
            subtitle="Active contacts"
            loading={statsLoading}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Recent Activity"
            value={stats?.recent_messages || 0}
            icon={<TrendingUp />}
            color="#075E54"
            subtitle="Last 24 hours"
            loading={statsLoading}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Response Rate"
            value="94%"
            icon={<Schedule />}
            color="#34B7F1"
            subtitle="Auto responses"
            loading={false}
          />
        </Grid>

        {/* WhatsApp Status */}
        <Grid item xs={12} md={6}>
          <WhatsAppStatusCard />
        </Grid>

        {/* Recent Messages */}
        <Grid item xs={12} md={6}>
          <RecentMessagesCard />
        </Grid>

        {/* Message Flow Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Message Flow
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={messageFlowData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="messages" fill="#25D366" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Message Categories */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Message Categories
              </Typography>
              {categoryData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  No classification data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item>
                <Chip
                  label="Send Broadcast"
                  color="primary"
                  onClick={() => window.location.href = '/broadcast'}
                  clickable
                />
              </Grid>
              <Grid item>
                <Chip
                  label="Manage Auto-Responses"
                  color="secondary"
                  onClick={() => window.location.href = '/auto-responses'}
                  clickable
                />
              </Grid>
              <Grid item>
                <Chip
                  label="View Analytics"
                  variant="outlined"
                  onClick={() => window.location.href = '/analytics'}
                  clickable
                />
              </Grid>
              <Grid item>
                <Chip
                  label="Settings"
                  variant="outlined"
                  onClick={() => window.location.href = '/settings'}
                  clickable
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;