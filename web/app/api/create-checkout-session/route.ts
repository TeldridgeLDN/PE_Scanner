import { NextRequest, NextResponse } from 'next/server';
import { currentUser } from '@clerk/nextjs/server';
import Stripe from 'stripe';

function getStripe() {
  return new Stripe(process.env.STRIPE_SECRET_KEY!, {
    apiVersion: '2025-11-17.clover',
  });
}

export async function POST(request: NextRequest) {
  const stripe = getStripe();
  try {
    // Check authentication
    const user = await currentUser();
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Parse request body
    const body = await request.json();
    const { priceId, plan } = body;

    if (!priceId || !plan) {
      return NextResponse.json(
        { error: 'Missing priceId or plan' },
        { status: 400 }
      );
    }

    // Create Stripe checkout session
    const session = await stripe.checkout.sessions.create({
      customer_email: user.emailAddresses[0]?.emailAddress,
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?success=true`,
      cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/#pricing`,
      metadata: {
        userId: user.id,
        plan: plan,
      },
      subscription_data: {
        metadata: {
          userId: user.id,
          plan: plan,
        },
      },
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Stripe checkout error:', error);
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}

