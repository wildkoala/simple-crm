import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import * as api from '@/lib/api';
import { Plus, Search, Mail, Phone, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function ContactsList() {
  const [searchQuery, setSearchQuery] = useState('');
  const [contacts, setContacts] = useState<api.Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    try {
      const data = await api.getContacts();
      setContacts(data);
    } catch (error) {
      toast.error('Failed to load contacts');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredContacts = contacts.filter((contact) => {
    const query = searchQuery.toLowerCase();
    return (
      contact.first_name.toLowerCase().includes(query) ||
      contact.last_name.toLowerCase().includes(query) ||
      contact.email.toLowerCase().includes(query) ||
      contact.organization.toLowerCase().includes(query)
    );
  });

  const getContactTypeBadge = (type: string) => {
    const variants = {
      individual: 'default',
      government: 'secondary',
      other: 'outline',
    } as const;
    return variants[type as keyof typeof variants] || 'outline';
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      cold: 'secondary',
      warm: 'default',
      hot: 'destructive',
    } as const;
    return variants[status as keyof typeof variants] || 'outline';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Contacts</h2>
            <p className="text-muted-foreground">
              Manage your contact relationships
            </p>
          </div>
          <Button asChild>
            <Link to="/contacts/new">
              <Plus className="mr-2 h-4 w-4" />
              Add Contact
            </Link>
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search contacts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Contacts Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : filteredContacts.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredContacts.map((contact) => (
              <Link key={contact.id} to={`/contacts/${contact.id}`}>
                <Card className="p-6 transition-shadow hover:shadow-md">
                  <div className="space-y-3">
                    <div>
                      <h3 className="font-semibold">
                        {contact.first_name} {contact.last_name}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {contact.organization}
                      </p>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Mail className="h-3 w-3" />
                        {contact.email}
                      </div>
                      {contact.phone && (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Phone className="h-3 w-3" />
                          {contact.phone}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between gap-2">
                      <div className="flex gap-2">
                        <Badge variant={getContactTypeBadge(contact.contact_type)}>
                          {contact.contact_type}
                        </Badge>
                        <Badge variant={getStatusBadge(contact.status)}>
                          {contact.status}
                        </Badge>
                      </div>
                      {contact.last_contacted_at && (
                        <span className="text-xs text-muted-foreground">
                          Last: {new Date(contact.last_contacted_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <p className="text-muted-foreground">
              {searchQuery
                ? 'No contacts found matching your search.'
                : 'No contacts yet. Add your first contact to get started.'}
            </p>
          </Card>
        )}
      </div>
    </Layout>
  );
}
