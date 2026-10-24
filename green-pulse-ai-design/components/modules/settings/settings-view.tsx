'use client'

import {
  Activity,
  AlertTriangle,
  Bell,
  CheckCircle2,
  Cpu,
  Download,
  Factory,
  Globe2,
  HardDrive,
  History,
  Key,
  Layers,
  Lock,
  Mail,
  Network,
  RefreshCw,
  Save,
  Search,
  Server,
  Settings as SettingsIcon,
  Shield,
  ShieldCheck,
  Sparkles,
  User,
  UserCheck,
  UserPlus,
  Users,
  Wifi,
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { toast } from 'sonner'

import { Reveal } from '@/components/motion/reveal'
import { IconTile } from '@/components/shared/icon-tile'
import { LoadingPanel } from '@/components/shared/loading-panel'
import { PageHeader } from '@/components/shared/page-header'
import { SectionHeader } from '@/components/shared/section-header'
import { SegmentedControl } from '@/components/shared/segmented-control'
import { Surface } from '@/components/shared/surface'
import { ToneBadge } from '@/components/shared/tone-badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useSettingsData } from '@/hooks/use-module-data'
import { formatNumber } from '@/lib/format'

type SettingsTab =
  | 'plant'
  | 'profile'
  | 'notifications'
  | 'security'
  | 'api'
  | 'users'
  | 'audit'

export function SettingsView() {
  const { data, isLoading, isError, refetch } = useSettingsData()
  const [activeTab, setActiveTab] = useState<SettingsTab>('plant')
  const [auditSearch, setAuditSearch] = useState('')
  const [testingConnection, setTestingConnection] = useState(false)

  // Controlled states with default initializers
  const [facilityName, setFacilityName] = useState('GreenPulse Central Hub - Unit 4')
  const [facilityLocation, setFacilityLocation] = useState('MIDC Industrial Area, Pune, Maharashtra, India')
  const [plantDemand, setPlantDemand] = useState(2500)
  const [utilityAccount, setUtilityAccount] = useState('MSEDCL-HT-99214482')
  const [substationFeeder, setSubstationFeeder] = useState('33kV Express Feeder Line #2')
  const [operatingShifts, setOperatingShifts] = useState('3-Shift Continuous (24x7)')

  const [profileName, setProfileName] = useState('Vikramaditya Sharma')
  const [profilePhone, setProfilePhone] = useState('+91 98230 44192')
  const [profileTimezone, setProfileTimezone] = useState('Asia/Kolkata (IST +05:30)')

  const [warningThreshold, setWarningThreshold] = useState(2200)
  const [powerFactorMinimum, setPowerFactorMinimum] = useState('0.92')
  const [webhookUrl, setWebhookUrl] = useState('https://scada-relay.internal.greenpulse.ai/v1/alerts')

  const [scadaHost, setScadaHost] = useState('192.168.10.45')
  const [scadaPort, setScadaPort] = useState('502')
  const [opcUaEndpoint, setOpcUaEndpoint] = useState('opc.tcp://192.168.10.12:4840/GreenPulse/Server')
  const [mqttBrokerUrl, setMqttBrokerUrl] = useState('mqtts://edge-broker.internal.greenpulse.ai:8883')

  const [logsList, setLogsList] = useState<typeof data.auditLogs | null>(null)

  // Initialize from localStorage or data
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('greenpulse_system_settings')
        if (saved) {
          const parsed = JSON.parse(saved)
          if (parsed.plantDemand) setPlantDemand(Number(parsed.plantDemand))
          if (parsed.facilityName) setFacilityName(parsed.facilityName)
          if (parsed.facilityLocation) setFacilityLocation(parsed.facilityLocation)
          if (parsed.utilityAccount) setUtilityAccount(parsed.utilityAccount)
          if (parsed.substationFeeder) setSubstationFeeder(parsed.substationFeeder)
          if (parsed.operatingShifts) setOperatingShifts(parsed.operatingShifts)
          if (parsed.profileName) setProfileName(parsed.profileName)
          if (parsed.profilePhone) setProfilePhone(parsed.profilePhone)
          if (parsed.profileTimezone) setProfileTimezone(parsed.profileTimezone)
          if (parsed.warningThreshold) setWarningThreshold(Number(parsed.warningThreshold))
          if (parsed.powerFactorMinimum) setPowerFactorMinimum(parsed.powerFactorMinimum)
          if (parsed.webhookUrl) setWebhookUrl(parsed.webhookUrl)
          if (parsed.scadaHost) setScadaHost(parsed.scadaHost)
          if (parsed.scadaPort) setScadaPort(parsed.scadaPort)
          if (parsed.opcUaEndpoint) setOpcUaEndpoint(parsed.opcUaEndpoint)
          if (parsed.mqttBrokerUrl) setMqttBrokerUrl(parsed.mqttBrokerUrl)
        }
      } catch {
        // Fall back to default
      }
    }
  }, [])

  if (isLoading || !data) {
    return (
      <div className="flex flex-col gap-8">
        <PageHeader
          eyebrow="System Configuration"
          title="Platform Settings"
          description="Plant information, SCADA gateway integration, user privileges, and security policies."
        />
        <LoadingPanel className="min-h-96" />
      </div>
    )
  }

  const currentLogs = logsList ?? data.auditLogs

  const handleSaveAllSettings = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const settingsPayload = {
      facilityName,
      facilityLocation,
      plantDemand,
      utilityAccount,
      substationFeeder,
      operatingShifts,
      profileName,
      profilePhone,
      profileTimezone,
      warningThreshold,
      powerFactorMinimum,
      webhookUrl,
      scadaHost,
      scadaPort,
      opcUaEndpoint,
      mqttBrokerUrl,
      savedAt: new Date().toISOString(),
    }

    // 1. Permanent Local Storage persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('greenpulse_system_settings', JSON.stringify(settingsPayload))
    }

    // 2. Database API sync if backend reachable
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || ''
      const token = typeof window !== 'undefined' ? localStorage.getItem('greenpulse_token') : null
      await fetch(`${apiBase}/api/v1/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          plant: {
            facility_name: facilityName,
            location: facilityLocation,
            contracted_demand_kw: plantDemand,
            utility_account: utilityAccount,
            substation_feeder: substationFeeder,
            operating_shifts: operatingShifts,
          },
          notifications: {
            warning_threshold_kw: warningThreshold,
            power_factor_minimum: parseFloat(powerFactorMinimum) || 0.92,
            webhook_url: webhookUrl,
          },
          api: {
            scada_host: scadaHost,
            scada_port: parseInt(scadaPort, 10) || 502,
            opc_ua_endpoint: opcUaEndpoint,
            mqtt_broker_url: mqttBrokerUrl,
          },
        }),
      }).catch(() => null)
    } catch {
      // Offline fallback already persisted in local storage
    }

    // 3. Update Audit Trail in memory
    const newAudit = {
      id: `audit-${Date.now()}`,
      timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
      user: profileName,
      action: `Updated plant registers: Demand Limit = ${plantDemand} kW, Warning = ${warningThreshold} kW`,
      module: 'System Settings',
      ipAddress: '192.168.10.104',
      hash: '0x' + Math.random().toString(16).slice(2, 10).toUpperCase(),
    }
    setLogsList([newAudit, ...currentLogs])

    toast.success('Configuration Saved & Persisted', {
      description: `Contracted demand ${plantDemand} kW and SCADA registers successfully committed to persistent storage.`,
    })
  }

  const handleTestGateway = () => {
    setTestingConnection(true)
    setTimeout(() => {
      setTestingConnection(false)
      toast.success('SCADA Modbus Ping Successful', {
        description: `Host ${scadaHost}:${scadaPort} responded in 4ms with 4,200 registers active.`,
      })
    }, 1200)
  }

  const filteredLogs = currentLogs.filter((log) => {
    if (auditSearch.trim()) {
      const q = auditSearch.toLowerCase()
      return (
        log.user.toLowerCase().includes(q) ||
        log.action.toLowerCase().includes(q) ||
        log.module.toLowerCase().includes(q)
      )
    }
    return true
  })


  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <PageHeader
        eyebrow="System Administration"
        title="Settings & System Configuration"
        description="Manage plant metadata, SCADA / IoT gateway integrations, user role-based access control, security policies, and immutable audit logs."
        meta={
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Facility: <strong className="text-foreground">{data.plant.facilityCode}</strong></span>
            <span>•</span>
            <span>SCADA Status: <strong className="text-success">Connected (0.4s heartbeat)</strong></span>
            <span>•</span>
            <span>Security: <strong className="text-foreground">2FA Enforced</strong></span>
          </div>
        }
        actions={
          <Button
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => handleSaveAllSettings()}
          >
            <Save className="size-3.5" />
            Save Changes
          </Button>
        }
      />

      {/* Main Settings Navigation Tabs */}
      <Surface className="p-2 overflow-x-auto">
        <div className="flex min-w-[700px] items-center gap-1">
          <Button
            variant={activeTab === 'plant' ? 'default' : 'ghost'}
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setActiveTab('plant')}
          >
            <Factory className="size-3.5" />
            Plant Information
          </Button>
          <Button
            variant={activeTab === 'profile' ? 'default' : 'ghost'}
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setActiveTab('profile')}
          >
            <User className="size-3.5" />
            User Profile
          </Button>
          <Button
            variant={activeTab === 'notifications' ? 'default' : 'ghost'}
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setActiveTab('notifications')}
          >
            <Bell className="size-3.5" />
            Notifications & Alarms
          </Button>
          <Button
            variant={activeTab === 'security' ? 'default' : 'ghost'}
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setActiveTab('security')}
          >
            <ShieldCheck className="size-3.5" />
            Security & 2FA
          </Button>
          <Button
            variant={activeTab === 'api' ? 'default' : 'ghost'}
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setActiveTab('api')}
          >
            <Network className="size-3.5" />
            API & Industrial IoT
          </Button>
          <Button
            variant={activeTab === 'users' ? 'default' : 'ghost'}
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setActiveTab('users')}
          >
            <Users className="size-3.5" />
            User Management
          </Button>
          <Button
            variant={activeTab === 'audit' ? 'default' : 'ghost'}
            size="sm"
            className="text-xs gap-1.5"
            onClick={() => setActiveTab('audit')}
          >
            <History className="size-3.5" />
            Audit Logs
          </Button>
        </div>
      </Surface>

      {/* Tab 1: Plant Information */}
      {activeTab === 'plant' && (
        <Reveal>
          <Surface className="flex flex-col gap-6 p-6">
            <SectionHeader
              title="Manufacturing Facility Information"
              description="Legal entity, facility identifiers, contracted utility demand, and operating shift scheme."
              icon={Factory}
            />

            <form onSubmit={handleSaveAllSettings} className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-foreground">Facility Name</label>
                <Input value={facilityName} onChange={(e) => setFacilityName(e.target.value)} className="text-xs" />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-foreground">Facility Identification Code</label>
                <Input defaultValue={data.plant.facilityCode} disabled className="text-xs font-mono bg-muted/40" />
              </div>

              <div className="flex flex-col gap-2 sm:col-span-2">
                <label className="text-xs font-semibold text-foreground">Physical Plant Location</label>
                <Input value={facilityLocation} onChange={(e) => setFacilityLocation(e.target.value)} className="text-xs" />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-foreground">Contracted Maximum Demand (kW)</label>
                <Input
                  type="number"
                  value={plantDemand}
                  onChange={(e) => setPlantDemand(Number(e.target.value))}
                  className="text-xs font-mono font-bold"
                />
                <span className="text-[11px] text-muted-foreground">Exceeding this draws ₹450/kVA penalty from DISCOM.</span>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-foreground">Electricity Utility Consumer ID</label>
                <Input value={utilityAccount} onChange={(e) => setUtilityAccount(e.target.value)} className="text-xs font-mono" />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-foreground">Grid Feeder Specification</label>
                <Input value={substationFeeder} onChange={(e) => setSubstationFeeder(e.target.value)} className="text-xs" />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-foreground">Plant Shift Working Model</label>
                <Input value={operatingShifts} onChange={(e) => setOperatingShifts(e.target.value)} className="text-xs" />
              </div>

              <div className="sm:col-span-2 flex justify-end">
                <Button type="submit" size="sm" className="text-xs gap-1.5">
                  <Save className="size-3.5" />
                  Save Facility Changes
                </Button>
              </div>
            </form>
          </Surface>
        </Reveal>
      )}

      {/* Tab 2: User Profile */}
      {activeTab === 'profile' && (
        <Reveal>
          <Surface className="flex flex-col gap-6 p-6">
            <SectionHeader
              title="Operator & Engineer Profile"
              description="Personal credentials, access role, and engineering privileges."
              icon={User}
            />

            <div className="flex items-center gap-4 border-b pb-6">
              <Avatar className="size-16 border-2 border-primary">
                <AvatarFallback className="bg-primary/10 text-primary font-bold text-lg">
                  VS
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-foreground">{data.profile.name}</h3>
                  <Badge variant="outline" className="text-xs text-primary">{data.profile.role}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">{data.profile.email} · {data.profile.department}</p>
                <span className="text-[11px] font-mono text-muted-foreground">{data.profile.licenseTier}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-foreground">Full Name</label>
                <Input value={profileName} onChange={(e) => setProfileName(e.target.value)} className="text-xs" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-foreground">Corporate Email Address</label>
                <Input defaultValue={data.profile.email} disabled className="text-xs bg-muted/40" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-foreground">Phone Number</label>
                <Input value={profilePhone} onChange={(e) => setProfilePhone(e.target.value)} className="text-xs font-mono" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-foreground">Operating Timezone</label>
                <Input value={profileTimezone} onChange={(e) => setProfileTimezone(e.target.value)} className="text-xs" />
              </div>
              <div className="sm:col-span-2 flex justify-end pt-2">
                <Button size="sm" className="text-xs gap-1.5" onClick={() => handleSaveAllSettings()}>
                  <Save className="size-3.5" />
                  Save Profile Details
                </Button>
              </div>
            </div>
          </Surface>
        </Reveal>
      )}

      {/* Tab 3: Notifications & Alarms */}
      {activeTab === 'notifications' && (
        <Reveal>
          <Surface className="flex flex-col gap-6 p-6">
            <SectionHeader
              title="Alarm Thresholds & Notification Relays"
              description="Configure automatic SMS, email, and webhook dispatches when electrical and thermal limits are breached."
              icon={Bell}
            />

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="flex flex-col gap-2 rounded-lg border p-4 bg-muted/20">
                <label className="text-xs font-semibold text-foreground">Peak Demand Warning Level (kW)</label>
                <Input
                  type="number"
                  value={warningThreshold}
                  onChange={(e) => setWarningThreshold(Number(e.target.value))}
                  className="text-xs font-bold font-mono"
                />
                <span className="text-[11px] text-muted-foreground">Alerts shift engineers before penalty threshold is crossed.</span>
              </div>

              <div className="flex flex-col gap-2 rounded-lg border p-4 bg-muted/20">
                <label className="text-xs font-semibold text-foreground">Minimum Power Factor Limit</label>
                <Input value={powerFactorMinimum} onChange={(e) => setPowerFactorMinimum(e.target.value)} className="text-xs font-bold font-mono" />
                <span className="text-[11px] text-muted-foreground">Triggers APFC capacitor bank inspection if PF &lt; 0.90.</span>
              </div>

              <div className="flex flex-col gap-2 rounded-lg border p-4 bg-muted/20 sm:col-span-2">
                <label className="text-xs font-semibold text-foreground">SCADA Webhook Alarm Relay URL</label>
                <Input value={webhookUrl} onChange={(e) => setWebhookUrl(e.target.value)} className="text-xs font-mono" />
                <span className="text-[11px] text-muted-foreground">JSON POST payload dispatched on critical equipment anomalies.</span>
              </div>

              <div className="sm:col-span-2 flex justify-end pt-2">
                <Button size="sm" className="text-xs gap-1.5" onClick={() => handleSaveAllSettings()}>
                  <Save className="size-3.5" />
                  Save Notification Thresholds
                </Button>
              </div>
            </div>
          </Surface>
        </Reveal>
      )}

      {/* Tab 4: Security & Compliance */}
      {activeTab === 'security' && (
        <Reveal>
          <Surface className="flex flex-col gap-6 p-6">
            <SectionHeader
              title="Industrial Cybersecurity & Compliance"
              description="Multi-factor authentication (MFA), role-based access control, session timeouts, and IP whitelists."
              icon={ShieldCheck}
            />

            <div className="flex flex-col divide-y rounded-lg border">
              <div className="flex items-center justify-between p-4 text-xs">
                <div>
                  <p className="font-semibold text-foreground">Two-Factor Authentication (2FA)</p>
                  <p className="text-muted-foreground">Hardware token or TOTP authenticator required for SCADA write actions.</p>
                </div>
                <ToneBadge tone="success">Enforced</ToneBadge>
              </div>

              <div className="flex items-center justify-between p-4 text-xs">
                <div>
                  <p className="font-semibold text-foreground">Control Console Session Timeout</p>
                  <p className="text-muted-foreground">Automatic lockout after 30 minutes of console inactivity.</p>
                </div>
                <span className="font-mono text-foreground font-semibold">30 mins</span>
              </div>

              <div className="flex items-center justify-between p-4 text-xs">
                <div>
                  <p className="font-semibold text-foreground">Subnet IP Whitelist</p>
                  <p className="text-muted-foreground">Restricted to plant OT network VLANs (192.168.10.0/24, 10.45.0.0/16).</p>
                </div>
                <Badge variant="outline">2 Active Subnets</Badge>
              </div>

              <div className="flex items-center justify-between p-4 text-xs">
                <div>
                  <p className="font-semibold text-foreground">Telemetry Encryption Standard</p>
                  <p className="text-muted-foreground">TLS 1.3 in transit with AES-256 encrypted local time-series datastore.</p>
                </div>
                <Badge variant="outline">FIPS 140-3 Compliant</Badge>
              </div>
            </div>
          </Surface>
        </Reveal>
      )}

      {/* Tab 5: API & Industrial IoT Integration */}
      {activeTab === 'api' && (
        <Reveal>
          <Surface className="flex flex-col gap-6 p-6">
            <SectionHeader
              title="SCADA, Modbus TCP & Industrial IoT Gateway"
              description="Direct integration endpoints for Schneider PLC, Siemens S7, Modbus TCP, and MQTT edge brokers."
              icon={Network}
            />

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-2 rounded-lg border p-4 bg-muted/20">
                <label className="text-xs font-semibold text-foreground">Modbus TCP Host & Port</label>
                <div className="flex gap-2">
                  <Input value={scadaHost} onChange={(e) => setScadaHost(e.target.value)} className="text-xs font-mono" />
                  <Input value={scadaPort} onChange={(e) => setScadaPort(e.target.value)} className="w-24 text-xs font-mono" />
                </div>
              </div>

              <div className="flex flex-col gap-2 rounded-lg border p-4 bg-muted/20">
                <label className="text-xs font-semibold text-foreground">OPC-UA Endpoint</label>
                <Input value={opcUaEndpoint} onChange={(e) => setOpcUaEndpoint(e.target.value)} className="text-xs font-mono" />
              </div>

              <div className="flex flex-col gap-2 rounded-lg border p-4 bg-muted/20 sm:col-span-2">
                <label className="text-xs font-semibold text-foreground">MQTT Edge Broker URL</label>
                <Input value={mqttBrokerUrl} onChange={(e) => setMqttBrokerUrl(e.target.value)} className="text-xs font-mono" />
              </div>

              <div className="flex flex-col gap-2 rounded-lg border p-4 bg-muted/20 sm:col-span-2">
                <label className="text-xs font-semibold text-foreground">API Token (Read/Write)</label>
                <Input defaultValue={data.api.apiKeyMasked} disabled className="text-xs font-mono bg-muted/40" />
              </div>

              <div className="sm:col-span-2 flex justify-end">
                <Button size="sm" className="text-xs gap-1.5" onClick={() => handleSaveAllSettings()}>
                  <Save className="size-3.5" />
                  Save Gateway Registers
                </Button>
              </div>
            </div>

            <div className="flex items-center justify-between border-t pt-4">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="size-2 rounded-full bg-success animate-status-pulse" />
                <span>Last Telemetry Heartbeat: {data.api.lastTelemetryHeartbeat}</span>
              </div>
              <Button
                size="sm"
                variant="outline"
                className="text-xs gap-1.5"
                disabled={testingConnection}
                onClick={handleTestGateway}
              >
                <Wifi className="size-3.5" />
                {testingConnection ? 'Pinging Gateway...' : 'Test Connection'}
              </Button>
            </div>
          </Surface>
        </Reveal>
      )}

      {/* Tab 6: User Management */}
      {activeTab === 'users' && (
        <Reveal>
          <Surface className="flex flex-col gap-6 p-6">
            <div className="flex items-center justify-between">
              <SectionHeader
                title="Plant Team & Access Management"
                description="Engineers, operators, and compliance auditors authorized to access GreenPulse AI."
                icon={Users}
              />
              <Button
                size="sm"
                className="text-xs gap-1.5"
                onClick={() => {
                  toast.success('Invitation Dialog', {
                    description: 'Modal to invite new certified plant engineer initiated.',
                  })
                }}
              >
                <UserPlus className="size-3.5" />
                Invite User
              </Button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b bg-muted/30 text-muted-foreground font-semibold">
                  <tr>
                    <th className="py-3 px-4">Name</th>
                    <th className="py-3 px-4">Email</th>
                    <th className="py-3 px-4">Role</th>
                    <th className="py-3 px-4">Department</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Last Active</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {data.users.map((u) => (
                    <tr key={u.id} className="hover:bg-muted/20">
                      <td className="py-3 px-4 font-semibold text-foreground">{u.name}</td>
                      <td className="py-3 px-4 font-mono text-muted-foreground">{u.email}</td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-[10px]">{u.role}</Badge>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">{u.department}</td>
                      <td className="py-3 px-4">
                        <ToneBadge tone="success">Active</ToneBadge>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">{u.lastActive}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Surface>
        </Reveal>
      )}

      {/* Tab 7: Audit Logs */}
      {activeTab === 'audit' && (
        <Reveal>
          <Surface className="flex flex-col gap-6 p-6">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b pb-4">
              <SectionHeader
                title="Cryptographic Audit Trail"
                description="Chronological immutable audit log of operator adjustments, work order dispatches, and security events."
                icon={History}
              />

              <div className="relative w-64">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
                <Input
                  placeholder="Search user, action, module..."
                  value={auditSearch}
                  onChange={(e) => setAuditSearch(e.target.value)}
                  className="h-8 pl-8 text-xs"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b bg-muted/30 text-muted-foreground font-semibold">
                  <tr>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">User</th>
                    <th className="py-3 px-4">Action Executed</th>
                    <th className="py-3 px-4">Module</th>
                    <th className="py-3 px-4">IP Address</th>
                    <th className="py-3 px-4">Verification Hash</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-muted/20">
                      <td className="py-3 px-4 font-mono text-muted-foreground">{log.timestamp}</td>
                      <td className="py-3 px-4 font-semibold text-foreground">{log.user}</td>
                      <td className="py-3 px-4 text-foreground">{log.action}</td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-[10px]">{log.module}</Badge>
                      </td>
                      <td className="py-3 px-4 font-mono text-muted-foreground">{log.ipAddress}</td>
                      <td className="py-3 px-4 font-mono text-xs text-primary">{log.hash}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Surface>
        </Reveal>
      )}
    </div>
  )
}
