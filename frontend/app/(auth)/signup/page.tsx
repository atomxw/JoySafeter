import { env, isTruthy } from '@/lib/core/config/env'
import SignupForm from '@/app/(auth)/signup/signup-form'

export const dynamic = 'force-dynamic'

export default async function SignupPage() {

  if (isTruthy(env.DISABLE_REGISTRATION)) {
    return <div>Registration is disabled, please contact your admin.</div>
  }

  return (
    <SignupForm
    />
  )
}
