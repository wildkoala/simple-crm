import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import * as api from '@/lib/api';
import { Plus, Search, Calendar, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function ContractsList() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('active');
  const [contracts, setContracts] = useState<api.Contract[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const contractsData = await api.getContracts();
      setContracts(contractsData);
    } catch (error) {
      toast.error('Failed to load contracts');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredContracts = contracts
    .filter((contract) => {
      const query = searchQuery.toLowerCase();
      const matchesSearch =
        contract.title.toLowerCase().includes(query) ||
        contract.description.toLowerCase().includes(query);

      let matchesStatus = false;
      if (statusFilter === 'all') {
        matchesStatus = true;
      } else if (statusFilter === 'active') {
        matchesStatus = contract.status === 'prospective' || contract.status === 'in progress';
      } else {
        matchesStatus = contract.status === statusFilter;
      }

      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime());

  const getStatusBadge = (status: string) => {
    const variants = {
      prospective: 'outline',
      'in progress': 'default',
      submitted: 'secondary',
      'not a good fit': 'destructive',
    } as const;
    return variants[status as keyof typeof variants] || 'outline';
  };

  const isDeadlineNear = (deadline: string) => {
    const deadlineDate = new Date(deadline);
    const now = new Date();
    const sevenDaysFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    return deadlineDate <= sevenDaysFromNow && deadlineDate >= now;
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Contract Opportunities</h2>
            <p className="text-muted-foreground">
              Track government contract submissions
            </p>
          </div>
          <Button asChild>
            <Link to="/contracts/new">
              <Plus className="mr-2 h-4 w-4" />
              Add Contract
            </Link>
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search contracts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="prospective">Prospective</SelectItem>
              <SelectItem value="in progress">In Progress</SelectItem>
              <SelectItem value="submitted">Submitted</SelectItem>
              <SelectItem value="not a good fit">Not a Good Fit</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Contracts List */}
        {isLoading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : filteredContracts.length > 0 ? (
          <div className="space-y-4">
            {filteredContracts.map((contract) => (
              <Link key={contract.id} to={`/contracts/${contract.id}`}>
                <Card className="p-6 transition-shadow hover:shadow-md">
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold">{contract.title}</h3>
                        <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                          {contract.description}
                        </p>
                      </div>
                      <Badge variant={getStatusBadge(contract.status)}>
                        {contract.status}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-6 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        Deadline: {new Date(contract.deadline).toLocaleDateString()}
                        {isDeadlineNear(contract.deadline) && (
                          <AlertCircle className="h-4 w-4 text-primary" />
                        )}
                      </div>
                      {contract.assigned_contacts && contract.assigned_contacts.length > 0 && (
                        <div>
                          Assigned to:{' '}
                          {contract.assigned_contacts
                            .map((c) => `${c.first_name} ${c.last_name}`)
                            .join(', ')}
                        </div>
                      )}
                    </div>

                    {contract.source && (
                      <p className="text-xs text-muted-foreground">
                        Source: {contract.source}
                      </p>
                    )}
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <p className="text-muted-foreground">
              {searchQuery || statusFilter !== 'active'
                ? 'No contracts found matching your filters.'
                : 'No active contracts yet. Add your first contract opportunity to get started.'}
            </p>
          </Card>
        )}
      </div>
    </Layout>
  );
}
