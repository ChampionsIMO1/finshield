'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast'
import { ShieldCheck, AlertTriangle, CreditCard, LogOut, Shield } from 'lucide-react'

interface Transaction {
    id: string
    merchant_name: string
    amount: number
    date: string
    category: string
    currency: string
}

interface FraudScore {
    transaction_id: string
    score: number
    is_flagged: boolean
    reasons: string[]
}

export default function DashboardPage() {
    const router = useRouter()
    const [transactions, setTransactions] = useState<Transaction[]>([])
    const [fraudScores, setFraudScores] = useState<FraudScore[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const token = localStorage.getItem('access_token')
        if (!token) {
            router.push('/login')
            return
        }
        fetchTransactions(token)
    }, [])

    const fetchTransactions = async (token: string) => {
        try {
            const res = await axios.get(
                `${process.env.NEXT_PUBLIC_API_URL}/transactions`,
                { headers: { Authorization: `Bearer ${token}` } }
            )
            setTransactions(res.data.transactions || [])
            setFraudScores(res.data.fraud_scores || [])
        } catch(err) {
            toast.error('Failed to load transactions')
        } finally {
            setLoading(false)
        }
    }

    const handleLogout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_id')
        router.push('/login')
    }

    const getFraudScore = (transactionId: string) => {
        return fraudScores.find(f => f.transaction_id === transactionId)
    }

    const flaggedCount = fraudScores.filter(f => f.is_flagged).length

    return (
        <div className="min-h-screen bg-gray-950 text-white">
            <Toaster />

            {/* Navbar */}
            <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <ShieldCheck className="text-blue-400" size={24} />
                    <span className="text-xl font-bold">SphinxGuard</span>
                </div>
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                >
                    <LogOut size={18} />
                    LogOut
                </button>
            </nav>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <CreditCard className="text-blue-400" size={20} />
                        <span className="text-gray-400 text-sm">Total Transactions</span>
                    </div>
                    <p className="text-3xl font-bold">{transactions.length}</p>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <AlertTriangle className="text-yellow-400" size={20} />
                        <span className="text-gray-400 text-sm">Flagged Transactions</span>
                    </div>
                    <p className="text-3xl font-bold text-yellow-400">{flaggedCount}</p>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <ShieldCheck className="text-green-400" size={20} />
                        <span className="text-gray-400 text-sm">Safe Transactions</span>
                    </div>
                    <p className="text-3xl font-bold text-green-400">
                        {transactions.length - flaggedCount}
                    </p>
                </div>
            </div>

            {/* Transactions */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl">
                <div className="px-6 py-4 border-b border-gray-800">
                    <h2 className="font-semibold text-lg">Recent Transactions</h2>
                </div>
            
            {loading ? (
                <div className="px-6 py-12 text-center text-gray-400">
                    Loading Transactions...
                </div>
            ) : transactions.length === 0 ? (
                <div className="px-6 py-12 text-center text-gray-400">
                    No Transactions Yet. Connect Your Bank To Get Started.
                </div>
            ) : (
                <div className="divide-y divide-gray-800">
                    {transactions.map(tx => {
                        const fraud = getFraudScore(tx.id)
                        return (
                            <div key={tx.id} className="px-6 py-4 flex items-center justify-between">
                                <div>
                                    <p className="font-medium">{tx.merchant_name || 'Unknown Merchant'}</p>
                                    <p className="text-sm text-gray-400">{tx.category} · {tx.date}</p>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="font-medium">
                                        {tx.currency} {tx.amount.toFixed(2)}
                                    </span>
                                    {fraud && (
                                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${fraud.is_flagged ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                                            {fraud.is_flagged ? '⚠ Flagged' : '✓ Safe'}
                                        </span>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}
            </div>
        </div>
    )
}