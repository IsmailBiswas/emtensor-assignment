export function formatInr(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatCrore(amount: number): string {
  const crore = amount / 10_000_000
  return `₹${crore.toFixed(crore >= 10 ? 1 : 2)} Cr`
}
