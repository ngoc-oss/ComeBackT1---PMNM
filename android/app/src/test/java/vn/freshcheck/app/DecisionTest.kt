// SPDX-License-Identifier: MIT
// FreshCheck source is licensed under MIT; see LICENSE at repository root.
package vn.freshcheck.app
import org.junit.Assert.*
import org.junit.Test

class DecisionTest {
    @Test fun uncertainIsNotSuspicious() {
        assertNull(Decision.choose(floatArrayOf(.34f,.35f,.31f),.7f))
        assertEquals(1,Decision.choose(floatArrayOf(.1f,.8f,.1f),.7f))
    }
    @Test fun spoiledAndFreshMapping() {
        assertEquals("HƯ",Decision.title(Decision.choose(floatArrayOf(.02f,.03f,.95f),.7f)))
        assertEquals("TƯƠI",Decision.title(Decision.choose(floatArrayOf(.8f,.1f,.1f),.7f)))
    }
    @Test(expected=IllegalArgumentException::class) fun rejectsInvalidOutput() {
        Decision.choose(floatArrayOf(Float.NaN,0f,0f),.7f)
    }
}
