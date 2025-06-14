import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const RegisterForm = () => {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email || !username || !password || !confirmPassword) {
            setError('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        try {
            setError('');
            setLoading(true);
            await register(email, password, username);
        } catch (error) {
            setError('Failed to create account: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
            <div className="bg-gray-800 p-8 rounded-lg shadow-xl w-full max-w-md">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Create an account</h2>
                    <p className="text-gray-400">Join the conversation today!</p>
                </div>

                {error && (
                    <div className="bg-red-600 text-white p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2">
                            EMAIL
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                            placeholder="Enter your email"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2">
                            USERNAME
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                            placeholder="Enter your username"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2">
                            PASSWORD
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                            placeholder="Enter your password"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2">
                            CONFIRM PASSWORD
                        </label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                            placeholder="Confirm your password"
                            disabled={loading}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-medium py-2 px-4 rounded transition duration-200"
                    >
                        {loading ? 'Creating Account...' : 'Continue'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-gray-400 text-sm">
                        Already have an account?{' '}
                        <Link
                            to="/login"
                            className="text-blue-400 hover:text-blue-300 underline"
                        >
                            Log In
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default RegisterForm; 