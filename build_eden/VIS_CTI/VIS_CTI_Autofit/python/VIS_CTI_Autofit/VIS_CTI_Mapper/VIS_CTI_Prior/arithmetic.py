class ArithmeticMixin:
    def __add__(self, other):
        """
        Add this object to another object. Addition occurs
        after priors have been converted into values.

        Parameters
        ----------
        other

        Returns
        -------
        An object comprising two objects to be summed after
        realisation
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.compound import SumPrior

        return SumPrior(self, other)

    def __abs__(self):
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.compound import AbsolutePrior

        return AbsolutePrior(self)

    def __radd__(self, other):
        """
        Add this object to another object. Addition occurs
        after priors have been converted into values.

        Parameters
        ----------
        other

        Returns
        -------
        An object comprising two objects to be summed after
        realisation
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.compound import SumPrior

        return SumPrior(other, self)

    def __sub__(self, other):
        """
        Subtract another object from this object. Subtraction
        occurs after priors have been converted into values.

        Parameters
        ----------
        other

        Returns
        -------
        An object comprising two objects to be summed after
        realisation
        """
        return self + (-other)

    def __neg__(self):
        """
        Returns an object representing the negation of this
        object.
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.compound import NegativePrior

        return NegativePrior(self)

    def __gt__(self, other_prior):
        """
        Add an assertion that values associated with this prior are greater.

        Parameters
        ----------
        other_prior
            Another prior which is associated with a field that should always have
            lower physical values.

        Returns
        -------
        An assertion object
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.assertion import (
            GreaterThanLessThanAssertion,
            unwrap,
        )

        return GreaterThanLessThanAssertion(
            greater=unwrap(self), lower=unwrap(other_prior)
        )

    def __lt__(self, other_prior):
        """
        Add an assertion that values associated with this prior are lower.

        Parameters
        ----------
        other_prior
            Another prior which is associated with a field that should always have
            greater physical values.

        Returns
        -------
        An assertion object
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.assertion import (
            GreaterThanLessThanAssertion,
            unwrap,
        )

        return GreaterThanLessThanAssertion(
            lower=unwrap(self), greater=unwrap(other_prior)
        )

    def __ge__(self, other_prior):
        """
        Add an assertion that values associated with this prior are greater or equal.

        Parameters
        ----------
        other_prior
            Another prior which is associated with a field that should always have
            lower physical values.

        Returns
        -------
        An assertion object
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.assertion import (
            GreaterThanLessThanEqualAssertion,
            unwrap,
        )

        return GreaterThanLessThanEqualAssertion(
            greater=unwrap(self), lower=unwrap(other_prior)
        )

    def __le__(self, other_prior):
        """
        Add an assertion that values associated with this prior are lower or equal.

        Parameters
        ----------
        other_prior
            Another prior which is associated with a field that should always have
            greater physical values.

        Returns
        -------
        An assertion object
        """
        from VIS_CTI_Autofit.VIS_CTI_Mapper.VIS_CTI_Prior.assertion import (
            GreaterThanLessThanEqualAssertion,
            unwrap,
        )

        return GreaterThanLessThanEqualAssertion(
            lower=unwrap(self), greater=unwrap(other_prior)
        )
