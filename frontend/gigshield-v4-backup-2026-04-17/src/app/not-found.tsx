import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4"
      style={{ background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)' }}>
      <p className="text-7xl mb-6">🛵</p>
      <h1 className="text-4xl font-black text-white mb-3">Page Not Found</h1>
      <p className="text-white/50 mb-8 max-w-md">
        Looks like this route took a wrong turn. Head back to safety.
      </p>
      <Link href="/"
        className="px-8 py-3 rounded-full font-bold bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:opacity-90 transition-all">
        Back to TriggerPe →
      </Link>
    </div>
  );
}
