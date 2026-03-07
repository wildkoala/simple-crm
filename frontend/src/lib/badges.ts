// Shared badge variant mappings for contacts and contracts

export function getContactStatusBadge(status: string) {
  const variants = {
    cold: 'secondary',
    warm: 'default',
    hot: 'destructive',
  } as const;
  return variants[status as keyof typeof variants] || 'outline';
}

export function getContactTypeBadge(type: string) {
  const variants = {
    individual: 'default',
    government: 'secondary',
    commercial: 'outline',
  } as const;
  return variants[type as keyof typeof variants] || 'outline';
}

export function getContractStatusBadge(status: string) {
  const variants = {
    prospective: 'outline',
    'in progress': 'default',
    submitted: 'secondary',
    'not a good fit': 'destructive',
  } as const;
  return variants[status as keyof typeof variants] || 'outline';
}
