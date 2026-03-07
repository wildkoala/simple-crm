import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import * as api from '@/lib/api';
import { getOpportunityStageBadge, formatCurrency, formatSetAside } from '@/lib/badges';
import { ArrowLeft, Trash2, Save, Loader2, Edit, X } from 'lucide-react';
import { toast } from 'sonner';

const STAGES = ['identified', 'qualified', 'capture', 'teaming', 'proposal', 'submitted', 'awarded', 'lost'] as const;
const SET_ASIDES = ['small_business', '8a', 'hubzone', 'wosb', 'sdvosb', 'full_and_open', 'none'] as const;
const SOURCES = ['sam_gov', 'agency_forecast', 'incumbent_recompete', 'partner_referral', 'internal'] as const;

const emptyOpp: api.Opportunity = {
  id: '', title: '', agency: '', naics_code: '', stage: 'identified',
  notes: '', created_at: '', updated_at: '', vehicle_ids: [], vehicles: [],
  estimated_value: undefined, win_probability: undefined,
};

export default function OpportunityDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [opp, setOpp] = useState<api.Opportunity | null>(null);
  const [editForm, setEditForm] = useState<api.Opportunity | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const loadData = useCallback(async () => {
    try {
      if (id === 'new') {
        setOpp(emptyOpp);
        setEditForm({ ...emptyOpp });
        setIsEditing(true);
      } else if (id) {
        const data = await api.getOpportunity(id);
        setOpp(data);
      }
    } catch (error) {
      toast.error('Failed to load opportunity');
      console.error(error);
      navigate('/opportunities');
    } finally {
      setIsLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleSave = async () => {
    if (!editForm) return;
    if (!editForm.title.trim()) { toast.error('Please enter a title'); return; }

    setIsSaving(true);
    try {
      const data: api.OpportunityCreate = {
        title: editForm.title,
        agency: editForm.agency || undefined,
        account_id: editForm.account_id || undefined,
        naics_code: editForm.naics_code || undefined,
        set_aside_type: editForm.set_aside_type || undefined,
        estimated_value: editForm.estimated_value || undefined,
        solicitation_number: editForm.solicitation_number || undefined,
        source: editForm.source || undefined,
        stage: editForm.stage,
        capture_manager_id: editForm.capture_manager_id || undefined,
        expected_release_date: editForm.expected_release_date || undefined,
        proposal_due_date: editForm.proposal_due_date || undefined,
        award_date_estimate: editForm.award_date_estimate || undefined,
        win_probability: editForm.win_probability ?? undefined,
        notes: editForm.notes,
        vehicle_ids: editForm.vehicle_ids,
      };

      if (id === 'new') {
        const created = await api.createOpportunity(data);
        toast.success('Opportunity created');
        navigate(`/opportunities/${created.id}`);
      } else {
        const updated = await api.updateOpportunity(editForm.id, data);
        setOpp(updated);
        setIsEditing(false);
        setEditForm(null);
        toast.success('Opportunity updated');
      }
    } catch (error) {
      toast.error('Failed to save opportunity');
      console.error(error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!opp) return;
    try {
      await api.deleteOpportunity(opp.id);
      toast.success('Opportunity deleted');
      navigate('/opportunities');
    } catch (error) {
      toast.error('Failed to delete');
      console.error(error);
    }
  };

  if (isLoading) {
    return <Layout><div className="flex items-center justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div></Layout>;
  }

  if (!opp && !isEditing) return null;
  const display = isEditing ? editForm : opp;
  if (!display) return null;

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" asChild>
              <Link to="/opportunities"><ArrowLeft className="h-4 w-4" /></Link>
            </Button>
            <h2 className="text-3xl font-bold tracking-tight">
              {id === 'new' ? 'New Opportunity' : display.title}
            </h2>
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : <><Save className="mr-2 h-4 w-4" />Save</>}
                </Button>
                {id !== 'new' && (
                  <Button variant="outline" onClick={() => { setEditForm(null); setIsEditing(false); }}>
                    <X className="mr-2 h-4 w-4" />Cancel
                  </Button>
                )}
              </>
            ) : (
              <>
                <Button onClick={() => { setEditForm({ ...opp! }); setIsEditing(true); }}>
                  <Edit className="mr-2 h-4 w-4" />Edit
                </Button>
                <Button variant="destructive" onClick={() => setShowDeleteConfirm(true)}>
                  <Trash2 className="mr-2 h-4 w-4" />Delete
                </Button>
              </>
            )}
          </div>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Opportunity Details</CardTitle>
              {!isEditing && <Badge variant={getOpportunityStageBadge(display.stage)}>{display.stage}</Badge>}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {isEditing ? (
              <>
                <div className="space-y-2">
                  <Label>Title</Label>
                  <Input value={editForm!.title} onChange={(e) => setEditForm({ ...editForm!, title: e.target.value })} placeholder="Opportunity title" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Agency</Label>
                    <Input value={editForm!.agency || ''} onChange={(e) => setEditForm({ ...editForm!, agency: e.target.value })} placeholder="e.g., Department of Defense" />
                  </div>
                  <div className="space-y-2">
                    <Label>Solicitation Number</Label>
                    <Input value={editForm!.solicitation_number || ''} onChange={(e) => setEditForm({ ...editForm!, solicitation_number: e.target.value })} />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Stage</Label>
                    <Select value={editForm!.stage} onValueChange={(v) => setEditForm({ ...editForm!, stage: v as api.Opportunity['stage'] })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {STAGES.map((s) => <SelectItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Set-Aside Type</Label>
                    <Select value={editForm!.set_aside_type || 'none'} onValueChange={(v) => setEditForm({ ...editForm!, set_aside_type: v as api.Opportunity['set_aside_type'] })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {SET_ASIDES.map((s) => <SelectItem key={s} value={s}>{formatSetAside(s)}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Source</Label>
                    <Select value={editForm!.source || 'internal'} onValueChange={(v) => setEditForm({ ...editForm!, source: v as api.Opportunity['source'] })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {SOURCES.map((s) => <SelectItem key={s} value={s}>{s.replace(/_/g, ' ')}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Estimated Value ($)</Label>
                    <Input type="number" value={editForm!.estimated_value ?? ''} onChange={(e) => setEditForm({ ...editForm!, estimated_value: e.target.value ? Number(e.target.value) : undefined })} />
                  </div>
                  <div className="space-y-2">
                    <Label>Win Probability (%)</Label>
                    <Input type="number" min="0" max="100" value={editForm!.win_probability ?? ''} onChange={(e) => setEditForm({ ...editForm!, win_probability: e.target.value ? Number(e.target.value) : undefined })} />
                  </div>
                  <div className="space-y-2">
                    <Label>NAICS Code</Label>
                    <Input value={editForm!.naics_code || ''} onChange={(e) => setEditForm({ ...editForm!, naics_code: e.target.value })} />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Expected Release Date</Label>
                    <Input type="date" value={editForm!.expected_release_date?.split('T')[0] || ''} onChange={(e) => setEditForm({ ...editForm!, expected_release_date: e.target.value || undefined })} />
                  </div>
                  <div className="space-y-2">
                    <Label>Proposal Due Date</Label>
                    <Input type="date" value={editForm!.proposal_due_date?.split('T')[0] || ''} onChange={(e) => setEditForm({ ...editForm!, proposal_due_date: e.target.value || undefined })} />
                  </div>
                  <div className="space-y-2">
                    <Label>Award Date Estimate</Label>
                    <Input type="date" value={editForm!.award_date_estimate?.split('T')[0] || ''} onChange={(e) => setEditForm({ ...editForm!, award_date_estimate: e.target.value || undefined })} />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Textarea value={editForm!.notes} onChange={(e) => setEditForm({ ...editForm!, notes: e.target.value })} rows={4} />
                </div>
              </>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <Label className="text-muted-foreground">Agency</Label>
                    <p className="mt-1">{display.agency || 'Not specified'}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Solicitation Number</Label>
                    <p className="mt-1">{display.solicitation_number || 'N/A'}</p>
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-6">
                  <div>
                    <Label className="text-muted-foreground">Estimated Value</Label>
                    <p className="mt-1 font-semibold text-lg">{formatCurrency(display.estimated_value)}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Win Probability</Label>
                    <p className="mt-1 font-semibold">{display.win_probability !== undefined && display.win_probability !== null ? `${display.win_probability}%` : 'N/A'}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Set-Aside</Label>
                    <p className="mt-1">{formatSetAside(display.set_aside_type)}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">NAICS</Label>
                    <p className="mt-1">{display.naics_code || 'N/A'}</p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-6">
                  <div>
                    <Label className="text-muted-foreground">Expected Release</Label>
                    <p className="mt-1">{display.expected_release_date ? new Date(display.expected_release_date).toLocaleDateString() : 'N/A'}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Proposal Due</Label>
                    <p className="mt-1 font-medium">{display.proposal_due_date ? new Date(display.proposal_due_date).toLocaleDateString() : 'N/A'}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Award Estimate</Label>
                    <p className="mt-1">{display.award_date_estimate ? new Date(display.award_date_estimate).toLocaleDateString() : 'N/A'}</p>
                  </div>
                </div>
                {display.source && (
                  <div>
                    <Label className="text-muted-foreground">Source</Label>
                    <p className="mt-1">{display.source.replace(/_/g, ' ')}</p>
                  </div>
                )}
                {display.vehicles && display.vehicles.length > 0 && (
                  <div>
                    <Label className="text-muted-foreground">Contract Vehicles</Label>
                    <div className="flex gap-2 mt-1">
                      {display.vehicles.map((v) => (
                        <Badge key={v.id} variant="outline">{v.name}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {display.notes && (
                  <div>
                    <Label className="text-muted-foreground">Notes</Label>
                    <p className="mt-1 whitespace-pre-wrap">{display.notes}</p>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
      <ConfirmDialog
        open={showDeleteConfirm}
        onOpenChange={setShowDeleteConfirm}
        onConfirm={handleDelete}
        title="Delete Opportunity"
        description="Are you sure you want to delete this opportunity? This action cannot be undone."
        confirmLabel="Delete"
      />
    </Layout>
  );
}
